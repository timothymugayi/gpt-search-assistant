import os
import logging
import sys

from langchain import (
    GoogleSearchAPIWrapper,
    WikipediaAPIWrapper,
    WolframAlphaAPIWrapper,
    SearxSearchWrapper
)

from configs import SearchConfigs
from rwmodels import ChatModelType

if True:
    os.environ["LANGCHAIN_HANDLER"] = "langchain"

from langchain.agents import Tool, load_tools
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.utilities import SerpAPIWrapper, BingSearchAPIWrapper
from langchain.agents import initialize_agent
from langchain.agents import AgentType

from coinmarketcap_search import CryptocurrencySearchAPIWrapper


logger = logging.getLogger(__name__)
settings = SearchConfigs()

if settings.debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


llm = ChatOpenAI(
    temperature=0,
    model_name=ChatModelType.GPT_4.value,
    max_retries=6,
    streaming=False,
    request_timeout=600
)


tools = load_tools(["llm-math"], llm=llm)


if settings.search_by_searx:
    searx_search = SearxSearchWrapper(
        searx_host="http://localhost:8080",
        unsecure=True,
        engines=["google"],
        categories=["news"]
    )
    # Test if everything is working if your docker-compose instance is up and running
    # "http://localhost:8080/search?q=10+Tips+for+Improving+Your+Coding+With+ChatGPT&engines=google&lang=en"
    # take not _searx_api_query is a protected class this is just a hack and yes doesn't conform to best OOP practises
    resp = searx_search._searx_api_query({
        "q": "10+Tips+for+Improving+Your+Coding+With+ChatGPT",
        "engines": "google",
        "lang": "en",
        "format": "json",
        "category": "general"
    })
    logger.debug(resp.results)

    tools.append(Tool(
        name="Searx Search",
        func=searx_search.run,
        description="A meta search engine."
                    "Useful for when you need to answer questions about current events."
                    "Input should be a search query."
    ))

if settings.search_by_serpi:
    google_search = SerpAPIWrapper(serpapi_api_key=os.environ["SERPER_API_KEY"])
    tools.append(Tool(
        name="Current Search",
        func=google_search.run,
        description="useful for when you need to answer questions about "
                    "current events or the current state of the world. "
                    "the input to this should be a single search term."
    ))

if settings.search_by_google:
    google_search_api = GoogleSearchAPIWrapper(
        google_api_key=os.environ["GOOGLE_API_KEY"],
        google_cse_id=os.environ["GOOGLE_CSE_ID"]
    )
    tools.append(Tool(
        name="Current Search",
        func=google_search_api.run,
        description="useful for when you need to answer questions about "
                    "current events or the current state of the world. "
                    "the input to this should be a single search term."
    ))

if settings.search_by_bing:
    bing_search_api = BingSearchAPIWrapper(bing_subscription_key=os.environ["BING_API_KEY"])
    tools.append(Tool(
        name="Current Search",
        func=bing_search_api.run,
        description="useful when you need to answer questions about the world around you."
    ))

if settings.search_by_wikipedia:
    wikipedia_search = WikipediaAPIWrapper()
    tools.append(Tool(
        name="Wikipedia",
        func=wikipedia_search.run,
        description="Useful for searching information on historical information on Wikipedia"
    ))

if settings.search_by_wolfram:
    wolfram_alpha = WolframAlphaAPIWrapper(wolfram_alpha_appid=os.environ["WOLFRAM_ALPHA_APPID"])
    tools.append(Tool(
        name="Wolfram Alpha",
        func=wolfram_alpha.run,
        description="Useful for when you need to answer questions about Math, "
                    "Science, Technology, Culture, people, Society and Everyday Life. "
                    "Input should be a search query"
    ))

if settings.search_by_coinmarketcap:
    crypto_search = CryptocurrencySearchAPIWrapper(coinmarketcap_api_key=os.environ["COINMARKETCAP_API_KEY"])
    tools.append(Tool(
        name="Crypto Currency Search",
        func=crypto_search.run,
        description="Use this tool when you need to answer questions about Cryptocurrency prices or altcoins prices "
                    "Input should be the Cryptocurrency coin name only or the ticker symbol"
    ))


memory = ConversationBufferMemory(memory_key="chat_history")
chain = initialize_agent(
    tools, llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=settings.debug,
    memory=memory,
    max_iterations=10
)


for tool in tools:
    print("Registered Langchain Agent: [{}]".format(tool.name))

print("\n")

while True:
    # a question that only searxng knows 'list top news headlines today'
    # a question coinmarketcap knows. list of last known prices for the following cryptocurrencies xrp, ftm, btc, cake, doge and mtv
    # a question that only wolframalpha knows 'Oscar for best actress 2023'
    # a question that only wikipedia may know 'who one the world cup in 2022'
    # a question that only coinmarketcap_search may know 'what is the last known bitcoin and xrp price'
    try:
        query_str = input("Please ask your question...")
        if query_str:
            if query_str.lower() == "exit":
                sys.exit(os.EX_OK)
            response = chain.run(query_str.strip())
            print(response)
    except ValueError as e:
        response = str(e)
        response_prefix = "Could not parse LLM output: `"
        if not response.startswith(response_prefix):
            raise e
        response_suffix = "`"
        if response.startswith(response_prefix):
            response = response[len(response_prefix):]
        if response.endswith(response_suffix):
            response = response[:-len(response_suffix)]
        print(response)
    except KeyboardInterrupt:
        exit(os.EX_OK)
