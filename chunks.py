from openai import OpenAI
from pinecone import Pinecone
from dotenv import load_dotenv
import os

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

index = pc.Index("bglw")

# Function to generate embeddings using OpenAI
def generate_embeddings(text):
    response = client.embeddings.create(
        input=[text],
        model='text-embedding-3-small'  # Choose the appropriate model for embeddings
    )
    embeddings = response.data[0].embedding
    return embeddings


# Generate and store embeddings in Pinecone
for i, text in enumerate(bungalow_information):
    embeddings = generate_embeddings(text)
    index.upsert(
        vectors=[{"id": f'doc{i}', "values": embeddings, "metadata": {"text": text}}],
    )
