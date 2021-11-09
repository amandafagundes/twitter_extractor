from dotenv import dotenv_values
from tweepy import OAuthHandler
from util import get_file_name, save
from util import date_to_str, format_tweet
import datetime
import json
import os
import sys
import tweepy

config = dotenv_values('.env')

search_queries = ['"virus chines"', '"virus da china"', '"variante indiana"', '"doença de velho"',
                'aborto assassinato', 'abortista']
# search_queries = ['#blacklivematters', '#pretosnopoder', '#negrosnopoder',
#                   '#racistasnãopassarão', '#negritude', '#blackpower"']
tweets_limit = 100

mode = 'EXTRACTION' # VALIDATION if terms are being validated
                    # EXTRACTION if the terms in search_queries have already been validated
                    
def load_api():
    consumer_key = config['CONSUMER_KEY']
    consumer_secret = config['CONSUMER_SECRET']
    access_token = config['ACCESS_TOKEN']
    access_secret = config['ACCESS_SECRET']

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_secret)

    # load the twitter API via tweepy
    return tweepy.API(auth)


def tweet_search(api, query, start, end):

    tweets = []
    while len(tweets) < tweets_limit:
        count = tweets_limit - len(tweets)

        try:
            new_tweets = api.search_tweets(q=query, count=count, locale='pt-BR',
                                           since_id=str(start), max_id=str(end-1), tweet_mode='extended')

            if bool(new_tweets):
                print('Yay!', len(new_tweets), ' tweets was found!')
                tweets.extend(new_tweets)
                end = new_tweets[-1].id
            else:
                print('No tweets found :(')
                break

        except Exception as e:
            print('Oops.. something went wrong: \n', e)
            break
    return tweets, end

# get the tweet tha will be used as seed to perform the search
# the query is a required field, so a common portuguese word is
# being used when the parameter isn't specified
def get_tweet_id(api, start_date=None, days_ago=9, query='e'):

    if start_date:  # use the given date to get the tweets
        tweet = api.search_tweets(q=query, count=10,
                                  locale='pt-BR', until=date_to_str(start_date))
    else:  # consider the last 9 days (the maximum allowed)
        search_date = datetime.datetime.now() - datetime.timedelta(days=days_ago)
        print('search_date:', search_date)
        tweet = api.search_tweets(q=query, count=10,
                                  locale='pt-BR',  until=date_to_str(search_date))

    return tweet[0].id

def get_since_and_max_id(json_file, min_days_old, max_days_old, api):

    read_IDs = False

    # if the same search has been performed before
    if os.path.isfile(json_file):
        print('Appending tweets to file named: ', json_file)
        read_IDs = True

    # set the 'starting point' ID for tweet collection
    if read_IDs:
        # open the json file and get the latest tweet ID
        with open(json_file, 'r') as f:
            lines = f.readlines()
            max_id = json.loads(lines[-1])['id']
            print('Searching from the bottom ID in file')
    else:
        # get the ID of a tweet that is min_days_old
        if min_days_old == 0:
            max_id = -1
        else:
            max_id = get_tweet_id(api, days_ago=(min_days_old-1))

    # set the smallest ID to search for
    since_id = get_tweet_id(api, days_ago=(max_days_old-1))

    print('max id (starting point) =', max_id)
    print('since id (ending point) =', since_id)

    return since_id, max_id

def main():

    # loop over search items,
    # creating a new file for each
    for query in search_queries:
        print(f'**** {query} ****')

        # authorize and load the twitter API
        json_file = get_file_name(query, 7, 1, custom_path='data/bias')
        api = load_api()

        since_id, max_id = get_since_and_max_id(json_file, 1, 7, api)

        start = datetime.datetime.now()
        end = start + datetime.timedelta(hours=2)
        count, exitcount = 0, 0

        while datetime.datetime.now() < end:

            tweets, max_id = tweet_search(api, query, since_id, max_id)
            # write tweets to file in JSON format
            if tweets:
                save(tweets, json_file, mode)
                exitcount = 0
            else:
                exitcount += 1
                if exitcount == 3:
                    if query == search_queries[-1]:
                        sys.exit(
                            'Maximum number of empty tweet strings reached - exiting')
                    else:
                        print(
                            'Maximum number of empty tweet strings reached - breaking')
                        break
            count += 1


if __name__ == "__main__":
    main()
