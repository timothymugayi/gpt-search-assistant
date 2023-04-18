from pydantic import BaseSettings


class SearchConfigs(BaseSettings):
    # Application
    search_by_wolfram = False
    search_by_serpi = False
    search_by_google = True
    search_by_wikipedia = False
    search_by_bing = False
    search_by_coinmarketcap = False
    search_by_searx = False
    debug = False

    class Config:
        env_prefix = 'my_prefix_'  # defaults to no prefix, i.e. ""
