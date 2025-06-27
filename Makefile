.ONESHELL:
.PHONY: test

# Detect OS and set conda activation accordingly
ifeq ($(OS),Windows_NT)
    CONDA_ACTIVATE = conda activate
else
    SHELL = /bin/bash  # If you are on MacOS you may need to change this to zsh
    CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate
endif

# Name of the conda environment
ENV_NAME=eddy
PROFILE=example
FIELD=quick_run
QUERY=example_meshgrid
DIM=20

# Create the conda environment with Python 3.11 and install dependencies
install:
	conda create --name $(ENV_NAME) python=3.11 -y && $(CONDA_ACTIVATE) $(ENV_NAME) && pip install -r requirements.txt

# Create new field and query
run:
	$(CONDA_ACTIVATE) $(ENV_NAME) && python ./src/main.py new -p $(PROFILE) -n $(FIELD) -d $(DIM) $(DIM) $(DIM) && python ./src/main.py query -n $(FIELD) -q $(QUERY)

test:
	$(CONDA_ACTIVATE) $(ENV_NAME) && pytest --cov=src --cov-fail-under=95 -m "(unit or system) and not slow"

# Delete the conda environment
clean:
	conda env remove --name $(ENV_NAME) -y