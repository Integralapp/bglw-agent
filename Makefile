# Define variables
VENV = venv
REQ = requirements.txt

# Default target
.PHONY: all
all: install

# Create a virtual environment
.PHONY: venv
venv:
	python3 -m venv $(VENV)

# Install requirements in the virtual environment
.PHONY: install
install: venv
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r $(REQ)

# Clean the virtual environment
.PHONY: clean
clean:
	rm -rf $(VENV)

# Add other targets as needed