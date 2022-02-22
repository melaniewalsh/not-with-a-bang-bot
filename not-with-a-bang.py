from twython import Twython, TwythonError
from secrets import *
import regex as re
from twarc import Twarc2, expansions
import datetime
import json
import sys
#Initialize Twitter bot
twitter_bot = Twython(app_key, app_secret, oauth_token, oauth_token_secret)

#Collect the most popular tweets that mention not with a bang
popular_results = twitter_bot.search(q="\"not with a bang\"", count=100, result_type="popular", tweet_mode="extended")

mixed_results = twitter_bot.search(q="\"not with a bang\"", count=100, result_type="mixed", tweet_mode="extended")

recent_results = twitter_bot.search(q="\"not with a bang\"", count=100, result_type="recent", tweet_mode="extended")

tweets = []
for tweet in popular_results['statuses']:
    tweets.append(tweet)
for tweet in mixed_results['statuses']:
    tweets.append(tweet)
for tweet in recent_results['statuses']:
    tweets.append(tweet)

# Replace your bearer token below
client = Twarc2(bearer_token=bearer_token)

# Specify the start time in UTC for the time period you want Tweets from
start_time = datetime.datetime(2009, 1, 1, 0, 0, 0, 0, datetime.timezone.utc)

# Specify the end time in UTC for the time period you want Tweets from
#end_time = datetime.datetime(2021, 5, 30, 0, 0, 0, 0, datetime.timezone.utc)


# The search_all method call the full-archive search endpoint to get Tweets based on the query, start and end times
search_results = client.search_all(query="\"not with a bang\"", start_time=start_time, max_results=100)


#Tweet counter to make sure that the bot only retweets one tweet every time the script runs
tweet_counter=0

#Look up previously tweeted IDs
#previously_quoted_tweet_ids = [tweet['quoted_status_id'] for tweet in twitter_bot.get_home_timeline()]
#Look up previously tweeted IDs
timeline_tweets = client.timeline("_notwithabang_")
previously_quoted_tweet_ids = []
for page in timeline_tweets:
    result = expansions.flatten(page)
    for tweet in result:
        if 'referenced_tweets' in tweet.keys():
            referenced_tweets = tweet['referenced_tweets']
            for referenced_tweet in referenced_tweets:
                #print(referenced_tweet['id'])
                previously_quoted_tweet_ids.append(referenced_tweet['id'])

#print(previouls)
#previously_quoted_tweet_ids = []
#for tweet in twitter_bot.get_home_timeline():
    #if 'quoted_status_id' in tweet:
        #previously_quoted_tweet_ids.append(tweet['quoted_status_id'])
        #print(tweet['quoted_status_id'])

#print(search_results)
#Function to make sure tweet mentions "James Baldwin"
def mentions_bang(status):
    # Remove capital letters and excessive whitespace/linebreaks
    test_text = ' '.join(status['full_text'].lower().split())
    test_text = re.sub(r'[^\w\s]','',test_text)
    #usernames = []
    #if status['user']['screen_name'] not in usernames and all(u not in status['text'] for u in usernames):
    #if 'not with a bang but' in test_text and 'whimper' not in test_text:
    #
    if 'not with a bang but' in test_text:
        return True
    else:
        return False

def mentions_bang_twitter_api(status):
    # Remove capital letters and excessive whitespace/linebreaks
    test_text = ' '.join(status.lower().split())
    test_text = re.sub(r'[^\w\s]','',test_text)
    #usernames = []
    #if status['user']['screen_name'] not in usernames and all(u not in status['text'] for u in usernames):
    #if 'not with a bang but' in test_text and 'whimper' not in test_text:
    #
    if 'not with a bang but' in test_text:
        return True
    else:
        return False
#Loop through search results
for tweet in tweets:

    if 'retweeted_status' in tweet.keys():
        followers_count = tweet['retweeted_status']['user']['followers_count']
        rt_count = tweet['retweeted_status']['retweet_count']
        tweet_text = tweet['retweeted_status']['full_text']
        user = tweet['retweeted_status']['user']['screen_name']
        retweet_id = tweet['retweeted_status']['id']
        tweet_id = tweet['id']
        verified = tweet['retweeted_status']['user']['verified']

        if str(retweet_id) not in previously_quoted_tweet_ids and str(tweet_id) not in previously_quoted_tweet_ids:

            if mentions_bang(tweet) == True:
                try:
                    if tweet_counter == 0:
                    #Check that tweets has more than 100 RTs
                        if  rt_count > 100:
                            #Retweet the tweet!
                            but_with_a = (re.search('(?<=not with a bang)[\s\S]*', tweet_text, re.IGNORECASE)).group()
                            but_with_a = but_with_a.replace('\n', '').lower()
                            but_with_a = re.sub(r'http\S+', '', but_with_a)
                            but_with_a = re.sub(r'[\'"”.,]','',but_with_a)
                            but_with_a = re.sub(r'^ ', '', but_with_a )

                            if len(but_with_a) > 164:
                                but_with_a = but_with_a[:161] + "..."
                                tweet_url = f'https://twitter.com/user/status/{retweet_id}'
                                new_tweet= f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}\n\n{tweet_url}'
                                print(new_tweet)
                                twitter_bot.update_status(status=new_tweet)
                                tweet_counter +=1
                                print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
                            else:
                                tweet_url = f'https://twitter.com/user/status/{retweet_id}'
                                new_tweet= f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}\n\n{tweet_url}'
                                print(new_tweet)
                                twitter_bot.update_status(status=new_tweet)
                                tweet_counter +=1
                                print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
                except TwythonError as e:
                    print(e)
                    print(f"ERROR! \n Tweet: {new_tweet} {tweet_text} \n Followers: {followers_count} \n URL: {tweet_url} \n RT:{rt_count}")
                    continue
    else:
        followers_count = tweet['user']['followers_count']
        rt_count = tweet['retweet_count']
        tweet_text = tweet['full_text']
        user = tweet['user']['screen_name']
        tweet_id = tweet['id']
        verified = tweet['user']['verified']

        if str(tweet_id) not in previously_quoted_tweet_ids:

            if mentions_bang(tweet) == True:
                try:
                    if tweet_counter == 0:
                    #Check that tweets has more than 100 RTs
                        if  rt_count > 100:
                            #Retweet the tweet!
                            but_with_a = (re.search('(?<=not with a bang)[\s\S]*', tweet_text, re.IGNORECASE)).group()
                            but_with_a = but_with_a.replace('\n', '').lower()
                            but_with_a = re.sub(r'http\S+', '', but_with_a)
                            but_with_a = re.sub(r'[\'"”.,]','',but_with_a)
                            but_with_a = re.sub(r'^ ', '', but_with_a )

                            if len(but_with_a) > 164:
                                but_with_a = but_with_a[:161] + "..."
                                tweet_url = f'https://twitter.com/user/status/{tweet_id}'
                                new_tweet= f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}\n\n{tweet_url}'
                                print(new_tweet)
                                twitter_bot.update_status(status=new_tweet)
                                tweet_counter +=1
                                print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
                            else:
                                tweet_url = f'https://twitter.com/user/status/{tweet_id}'
                                new_tweet= f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}\n\n{tweet_url}'
                                print(new_tweet)
                                twitter_bot.update_status(status=new_tweet)
                                tweet_counter +=1
                                print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
                except TwythonError as e:
                    print(e)
                    print(f"ERROR! \n Tweet: {new_tweet} {tweet_text} \n Followers: {followers_count} \n URL: {tweet_url} \n RT:{rt_count}")
                    continue

for page in search_results:
    result = expansions.flatten(page)
    for tweet in result:
        # Here we are printing the full Tweet object JSON to the console
        if 'referenced_tweets' in tweet.keys():
            referenced_tweets = tweet['referenced_tweets']
            for referenced_tweet in referenced_tweets:
            #print(tweet)
                if 'author' in referenced_tweet.keys():
                    followers_count = referenced_tweet['author']['public_metrics']['followers_count']
                    rt_count = referenced_tweet['public_metrics']['retweet_count']
                    tweet_text = referenced_tweet['text']
                    #user = tweet['retweeted_status']['user']['screen_name']
                    retweet_id = referenced_tweet['id']
                    tweet_id = tweet['id']
                    verified = referenced_tweet['author']['verified']

                    if str(retweet_id) not in previously_quoted_tweet_ids and str(tweet_id) not in previously_quoted_tweet_ids:

                        if mentions_bang_twitter_api(tweet_text) == True:
                            try:
                                if tweet_counter == 0:
                                #Check that tweets has more than 100 RTs
                                    if  rt_count > 100:
                                        #Retweet the tweet!
                                        but_with_a = (re.search('(?<=not with a bang)[\s\S]*', tweet_text, re.IGNORECASE)).group()
                                        but_with_a = but_with_a.replace('\n', '').lower()
                                        but_with_a = re.sub(r'http\S+', '', but_with_a)
                                        but_with_a = re.sub(r'[\'"”.,]','',but_with_a)
                                        but_with_a = re.sub(r'^ ', '', but_with_a )

                                        if len(but_with_a) > 164:
                                            but_with_a = but_with_a[:161] + "..."

                                            tweet_url = f'https://twitter.com/user/status/{retweet_id}'
                                            new_tweet= f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}\n\n{tweet_url}'
                                            print(new_tweet)
                                            twitter_bot.update_status(status=new_tweet)
                                            tweet_counter +=1
                                            print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
                                        else:
                                            tweet_url = f'https://twitter.com/{user}/status/{retweet_id}'
                                            new_tweet= f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}\n\n{tweet_url}'
                                            print(new_tweet)
                                            twitter_bot.update_status(status=new_tweet)
                                            tweet_counter +=1
                                            print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
                                    #Check that Twitter account has more than 1000 followers
                                    elif followers_count > 5000 or verified == True:
                                        #Retweet the tweet!
                                        but_with_a = (re.search('(?<=not with a bang)[\s\S]*', tweet_text, re.IGNORECASE)).group()
                                        but_with_a = but_with_a.replace('\n', '').lower()
                                        but_with_a = re.sub(r'http\S+', '', but_with_a)
                                        but_with_a = re.sub(r'[\'"”.,]','',but_with_a)
                                        but_with_a = re.sub(r'^ ', '', but_with_a )
                                        if len(but_with_a) > 164:
                                            but_with_a = but_with_a[:161] + "..."

                                            tweet_url = f'https://twitter.com/user/status/{retweet_id}'
                                            new_tweet= f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}\n{tweet_url}'

                                            twitter_bot.update_status(status=new_tweet)
                                            print(new_tweet)
                                            tweet_counter +=1
                                            print(f"✨Met follower threshold✨ Succesfully retweeted {tweet_text}!")
                                        else:
                                            tweet_url = f'https://twitter.com/user/status/{retweet_id}'
                                            new_tweet= f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}\n\n{tweet_url}'
                                            print(new_tweet)
                                            twitter_bot.update_status(status=new_tweet)
                                            tweet_counter +=1
                                            print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
                                else:
                                    print("Done tweeting")
                                    sys.exit(1)
                            except TwythonError as e:
                                print(e)
                                print(f"ERROR! \n Tweet: {new_tweet} {tweet_text} \n Followers: {followers_count} \n URL: {tweet_url} \n RT:{rt_count}")
                                continue
    else:
        followers_count = tweet['author']['public_metrics']['followers_count']
        rt_count = tweet['public_metrics']['retweet_count']
        tweet_text = tweet['text']
        #user = tweet['author']['screen_name']
        id = tweet['id']
        verified = tweet['author']['verified']

        if str(id) not in previously_quoted_tweet_ids:

            if mentions_bang_twitter_api(tweet_text) == True:
                try:
                    if tweet_counter == 0:
                    #Check that tweets has more than 100 RTs
                        if  rt_count > 100:
                            #Retweet the tweet!
                            but_with_a = (re.search('(?<=not with a bang)[\s\S]*', tweet_text, re.IGNORECASE)).group()
                            but_with_a = but_with_a.replace('\n', '').lower()
                            but_with_a = re.sub(r'http\S+', '', but_with_a)
                            but_with_a = re.sub(r'[\'"”.,]','',but_with_a)
                            but_with_a = re.sub(r'^ ', '', but_with_a )

                            if len(but_with_a) > 164:
                                but_with_a = but_with_a[:161] + "..."
                                tweet_url = f'https://twitter.com/user/status/{id}'
                                new_tweet= f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}\n\n{tweet_url}'
                                print(new_tweet)
                                twitter_bot.update_status(status=new_tweet)
                                tweet_counter +=1
                                print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
                            else:
                                tweet_url = f'https://twitter.com/user/status/{id}'
                                new_tweet= f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}\n\n{tweet_url}'
                                print(new_tweet)
                                twitter_bot.update_status(status=new_tweet)
                                tweet_counter +=1
                                print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
                        #Check that Twitter account has more than 1000 followers
                        elif followers_count > 5000 or verified == True:
                            #Retweet the tweet!
                            but_with_a = (re.search('(?<=not with a bang)[\s\S]*', tweet_text, re.IGNORECASE)).group()
                            but_with_a = but_with_a.replace('\n', '').lower()
                            but_with_a = re.sub(r'http\S+', '', but_with_a)
                            but_with_a = re.sub(r'[\'"”.,]','',but_with_a)
                            but_with_a = re.sub(r'^ ', '', but_with_a )
                            if len(but_with_a) > 164:
                                but_with_a = but_with_a[:161] + "..."
                                tweet_url = f'https://twitter.com/user/status/{id}'
                                new_tweet= f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}\n{tweet_url}'
                                twitter_bot.update_status(status=new_tweet)
                                print(new_tweet)
                                tweet_counter +=1
                                print(f"✨Met follower threshold✨ Succesfully retweeted {tweet_text}!")
                            else:
                                tweet_url = f'https://twitter.com/user/status/{id}'
                                new_tweet= f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}\n\n{tweet_url}'
                                print(new_tweet)
                                twitter_bot.update_status(status=new_tweet)
                                tweet_counter +=1
                                print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
                    else:
                        print("Done tweeting")
                        sys.exit(1)
                except TwythonError as e:
                    print(e)
                    print(f"ERROR! \n Tweet: {new_tweet} {tweet_text} \n Followers: {followers_count} \n URL: {tweet_url} \n RT:{rt_count}")
                    continue
