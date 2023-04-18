# LangChain Agent GPT Search Assistant

Example of how to use Langchain tool agents evlauate to GPT plugins 
to give your ChatGPT access to the internet. 

## Prerequisite packages 

The following are the additional packages to run LangChain Agent tools. 
You may refer to getting started section to install correct versions directly from the conda environment.yml file

```bash 
pip install python-coinmarketcap

pip install wolframalpha

pip install wikipedia

pip install google-api-python-client

pip install google-search-results

```
[coinmarketcap_search.py](coinmarketcap_search.py) file is a Crypto currency Wrapper 
to coinmarket cap to get the latest prices for over 9k cryptocurrency coins


If you make any updates to your conda environment environment you can re export the dependencies using 
this command 

```commandline
conda env export | grep -v "^prefix: " > environment.yml
```

# Getting Started 

1. install conda 
2. Create new conda environment based on yaml file 

```commandline
conda env create --file=environment.yml
```

# About SearxNG

SearxNG is a privacy-friendly free metasearch engine that aggregates results from
multiple search engines
https://docs.searxng.org/admin/engines/configured_engines.html and databases and
supports the `OpenSearch 
https://github.com/dewitt/opensearch/blob/master/opensearch-1-1-draft-6.md
specification.

You will need docker to run it from your local machine

follow instruction on git repo https://github.com/searxng/searxng-docker