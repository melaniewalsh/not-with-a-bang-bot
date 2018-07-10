#! /usr/bin/env python3

from twython import Twython, TwythonStreamer, TwythonError
from secrets import *
import re

# Initialize twython with relevant secret keys
api = Twython(app_key, app_secret, oauth_token, oauth_token_secret)

class MyStreamListener(TwythonStreamer):
    """
    This class defines how Twitter's streaming API should behave.
    """

    def on_success(self, status):
        """
        When a status is found, filter for the exact phrase and retweet.
        """
        if is_eliot(status): # Use function for testing the phrase
            if "RT @" not in status['text']:
                but_with_a = (re.search('(?<=not with a).*', status['text'], re.IGNORECASE)).group()
                user = status['user']['screen_name']
                id = status['id']
                tweet_url = f'https://twitter.com/{user}/status/{id}'
                tweet=f'Not with a{but_with_a} \n \n💥@{user}\n{tweet_url}'
                tweet = tweet.replace('”', '')
                tweet = tweet.replace('\'', '')
                tweet = tweet.replace('\"', '')
                try:
                    #api.retweet(id=status['id'])
                    #print(tweet)
                    api.update_status(status=tweet)
                except TwythonError:
                    pass

    def on_error(self, status_code, data):
        """
        When API returns error, keep going unless the error is for rate limit.
        """
        if status_code == 420:
            self.disconnect()


# List relevant queries
queries = ["not with a bang"]
queries = ','.join(queries)

def is_eliot(status):
    """
    Determines whether or not the tweet is a TS Eliot parody,
    using the same list of queries that the streaming API uses.
    """
    test_text = ' '.join(status['text'].lower().split()) # Remove capital letters and excessive whitespace/linebreaks
    usernames = ['notwithabangbot', 'NWABpod', '_bang_bot_'] # Block screen_names of known parody accounts
    if status['user']['screen_name'] not in usernames and all(u not in status['text'] for u in usernames):
        if 'not with a bang' in test_text: # Capture parodies of the form
            return True
        else:
            return False
    else:
        return False

# Initialize stream listener
stream = MyStreamListener(app_key, app_secret, oauth_token, oauth_token_secret) # Create class instance

while True:
	try:
		stream.statuses.filter(track=queries) # Listen for queries (case insensitive)
	except:
		continue


# The code below used for testing the custom tweet filter function
 #class status():
     #class user():
                #    screen_name = 'johnrladd'
     # text = 'I have eaten\n\nThe plums\n\nAnd which\n\nyou were probably not with a blank but with a blank'
     # text = 'Plums a little, talk a little, plums a little, talk a little, icebox icebox, icebox icebox'
     # text = 'Totally normal tweet without any reference'

 #status = status()
 #myStreamListener.on_status(status)
