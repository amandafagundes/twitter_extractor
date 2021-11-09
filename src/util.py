import os
import json
import datetime

def date_to_str(date):
    return '{0}-{1:0>2}-{2:0>2}'.format(date.year, date.month, date.day)

def format_tweet(nested_json):
    """
        Flatten json object with nested keys into a single level.
        Args:
            nested_json: A nested json object.
        Returns:
            The flattened json object if successful, None otherwise.
    """
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(nested_json)
    return out

def get_file_name(search_phrase, interval_end, interval_begin, custom_path='data/bias'):
    name = search_phrase.replace(' ', '_').replace('"', '')
    json_file_root = f'{custom_path}/{name}/{name}'

    os.makedirs(os.path.dirname(json_file_root), exist_ok=True)

    date_1 = datetime.datetime.now() - datetime.timedelta(days=interval_end-1)
    date_2 = datetime.datetime.now() - datetime.timedelta(days=interval_begin)
    day = date_1.strftime('%Y-%m-%d') + '_to_' + date_2.strftime('%Y-%m-%d')

    return f'{json_file_root}_{day}.json'

def save(tweets, filename, mode):
    isFile = False
    # remove the brackets ] at the end of file
    if os.path.isfile(filename):
        isFile = True
        lines = open(filename, 'r').readlines()
        last_line = lines[-1]
        last_line = ''.join(last_line.rsplit(']', 1))
        lines[-1] = last_line
        open(filename, 'w').writelines(lines)
        
    with open(filename, 'a') as f:
        if not isFile:
            f.write('[')
        for tweet in tweets:
            tweet_json = tweet._json
            if 'lang' in tweet_json and tweet_json['lang'] == 'pt':
                if mode == 'VALIDATION':
                    if 'retweeted_status' in tweet_json:
                        print(tweet_json['retweeted_status']['full_text'])
                    else:
                        print(tweet_json['full_text'])
                    resp = input('Is that a valid tweet? (Y/N)')
                    if resp.lower() == 'y':
                        json.dump(format_tweet(tweet_json), f)
                else:
                    json.dump(format_tweet(tweet_json), f)
                f.write(',\n')
        f.write(']')
