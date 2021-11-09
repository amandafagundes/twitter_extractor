# About

Script used to collect tweets data from Twitter API (adapted from  [this project](https://github.com/agalea91/twitter_search))

# Libraries

The tweepy library is used to collect data and to keep Twitter's credentials safe,  that data is provided from environment variables using the python-dotenv package.

# Project

The collected data is organized into `data` folder as JSON files in the format `{query}_{begin-date}_to_{end-date}` where `query` refers to the query used in the search and `begin-date` and `end-date` are the specified range.

To execute the extractor: `$ python3 src/search.py`