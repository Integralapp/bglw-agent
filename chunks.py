from urllib.parse import urljoin
from pinecone import Pinecone
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import os
import nltk
from urllib.parse import urljoin, urlparse
import time
from openai import OpenAI
import urllib
import re

nltk.download('punkt')

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OAI_API_KEY")
)
pc = Pinecone(api_key=os.getenv("PC_API_KEY"))

bungalow_information = ["Description: THE LATEST FLAGSHIP RESTAURANT FROM MICHELIN-STARRED CHEF VIKAS KHANNA AND NEW YORK’S BELOVED GUPSHUP BRINGS A ONE-OF-A-KIND EXPERIENCE. BUNGALOW INVITES YOU ON A JOURNEY THROUGH INDIA’S 28 STATES, WITH TIME-HONORED RECIPES AND REIMAGINED CLASSICS.",
"KISS OF KASHMIR: LOTUS ROOTS, KIDNEY BEANS, RADISH-WALNUT RAITA, PICKLED TURNIPS",
"SHRIMP BALCHAO CONES: SHELLFISH, EGGS, DAIRY, SESAME",
"WHITE PEAS GUGUNI: DATE -TAMARIND-MINT, CHICKPEA NOODLES, ROASTED CUMIN, MILK BUN",
"LAMB SEEKH KABAB: KUMQUAT PICKLE, PLUM CHUTNEY, PEANUT CRUMBLE, CHEESE FILLING", 
"CHICKEN CHITRANEE, HOMESTYLE CHICKEN CURRY, TOMATOES, TAMARIND, SHISHITO CHILI",
"EGGPLANT BHARTA: JAPANESE EGGPLANT, SMOKED ONIONS, PEAS, TOMATOES, CILANTRO ",
"SPICE ROASTED PINEAPPLE: COCONUT, LEMON, MUSTARD SEEDS, CURRY LEAVES",
"HYDERABADI CHICKEN BIRYANI: MINT, CRISPY ONIONS, SAFFRON", 
"AMRITSARI CHOLE: CHICKEA, SPICED ONION, GINGER POWDER, CORIANDER LEAF, TOMATO",
"ROSE KULFI: ROSE KULFI, GULKAND, BUTTERFLY PEA RABDI, WHITE CHOCOLATE BARK ",
"SAFFRON PANNA COTTA: THANDAI PANNA COTTA, SAFFRON, PISTACHIO MOUSSE, DRIED ROSE PETALS POWDER, MIXED NUTS ",
"CELEBRATION DESSERT: COCONUT, BANANA, JAGGERY-CARAMEL DRIZZLE ",
"LOCATION: 24 First Avenue, New York, NY 10009",
'''Hours
Tuesday / Wednesday / Sunday : 5PM - 11PM (Last seating 10PM)

Thursday / Friday / Saturday : 5PM - 12AM (Last seating 10:30PM)

Monday - Closed''',
"We kindly invite you to make your reservations through our online booking partner, Resy, every day exactly at 11AM EST. Please note that, at this time, we are unable to accept reservations over the phone or email. ",
"Given our limited capacity, we are working diligently to accommodate all of our guests to the best of our ability. To ensure a smooth operation in our kitchen and to provide you with the best possible service, we are currently limiting party sizes to a maximum of six to eight people.",
"For any inquiries or special requests, we recommend contacting us via email at info@bungalowny.com. While we cannot guarantee an immediate response, we will do our best to assist you. ",
"We strive to accommodate all reservation requests, but please keep in mind that we are currently assigning tables on a first-come, first-served basis through our online booking partner, Resy. In order to accomodate ADA accessiblity, please email us prior to your reservation stating name, date and time of your reservation. ",
"Additionally, please note that we do not carry highchairs and our space cannot accommodate strollers. Therefore, we strongly recommend that children 10 year of age or younger do not accompany you to Bungalow."
]

index = pc.Index("la")

# Function to generate embeddings using OpenAI
def generate_embeddings(text):
    response = client.embeddings.create(
        input=text,
        model='text-embedding-3-large'  # Choose the appropriate model for embeddings
    )
    embeddings = response.data[0].embedding
    return embeddings

def write_embeddings(chunks):
    # Generate and store embeddings in Pinecone
    for i, text in enumerate(chunks):
        print(f"Writing {i}th chunk: f{text[0:100]}...")
        embeddings = generate_embeddings(text)
        index.upsert(
            vectors=[{"id": f'doc{i}', "values": embeddings, "metadata": {"text": text}}],
        )

def split_text_into_chunks(text, chunk_size=500):
    sentences = nltk.tokenize.sent_tokenize(text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= chunk_size:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def is_file_url(url):
    # Parse the URL
    parsed_url = urllib.parse.urlparse(url)
    
    # Get the path component
    path = parsed_url.path
    
    # Remove query parameters and fragments
    path = re.sub(r'\?.*$', '', path)
    path = re.sub(r'#.*$', '', path)
    
    # Check if the path has a file extension
    return bool(re.search(r'\.[a-zA-Z0-9]+$', path))

def clean_url(url: str):
    return url.split('#')[0]

# Function to get all relative URLs on a page
def get_all_relative_urls(base_url, timeout=10):
    visited_urls = set()
    urls_to_visit = {base_url}
    all_text_chunks = set()

    while urls_to_visit:
        current_url = urls_to_visit.pop()
        visited_urls.add(current_url)

        print(f"Investigating: {current_url}")
        
        try:
            response = requests.get(current_url, timeout=timeout)
            
            backoff = 1
            while response.status_code == 429:
                print(f"Rate limit hit. Retrying in {backoff} seconds...")
                time.sleep(backoff)
                backoff *= 2
                response = requests.get(current_url, timeout=timeout)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Process text
            page_text = soup.get_text()
            text_chunks = set(split_text_into_chunks(page_text))
            all_text_chunks.update(text_chunks)
            print(f"Added {len(text_chunks)} new text chunks")

            # Process links
            for link in soup.find_all('a', href=True):
                full_url = clean_url(urljoin(base_url, link['href']))
                parsed_url = urlparse(full_url)
                if parsed_url.netloc == urlparse(base_url).netloc and not is_file_url(link["href"]):
                    if full_url not in visited_urls and full_url not in urls_to_visit:
                        urls_to_visit.add(full_url)
                        print(f"Found new URL to visit: {full_url}")
            
            print(f"Processed {current_url}. {len(urls_to_visit)} URLs left to visit.")
        
        except requests.Timeout:
            print(f"Timeout occurred while processing: {current_url}")
        except requests.RequestException as e:
            print(f"Request failed for {current_url}: {e}")
    
    print(f"Crawling complete. Processed {len(visited_urls)} URLs and collected {len(all_text_chunks)} unique text chunks.")
    return list(all_text_chunks)


def main():
    chunks = get_all_relative_urls("https://lealfre.com")
    write_embeddings(chunks)

if __name__ == "__main__":
    main()
