from twython import Twython, TwythonError
from secrets import *
import regex as re

#Initialize Twitter bot
twitter_bot = Twython(app_key, app_secret, oauth_token, oauth_token_secret)

#Collect the most popular tweets that mention not with a bang
popular_results = twitter_bot.search(q="\"not with a bang\"", count=100, result_type="popular", tweet_mode="extended")

mixed_results = twitter_bot.search(q="\"not with a bang\"", count=100, result_type="mixed", tweet_mode="extended")

recent_results = twitter_bot.search(q="\"not with a bang\"", count=100, result_type="recent", tweet_mode="extended")

#Tweet counter to make sure that the bot only retweets one tweet every time the script runs
tweet_counter=0

#Look up previously tweeted IDs
#previously_quoted_tweet_ids = [tweet['quoted_status_id'] for tweet in twitter_bot.get_home_timeline()]
#Look up previously tweeted IDs
previously_quoted_tweet_ids = []
for tweet in twitter_bot.get_home_timeline():
    if 'quoted_status_id' in tweet:
        previously_quoted_tweet_ids.append(tweet['quoted_status_id'])
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
    if 'not with a bang but' in test_text in test_text:
        return True
    else:
        return False

#Loop through search results
for tweet in popular_results["statuses"]:

    if 'retweeted_status' in tweet.keys():
        followers_count = tweet['retweeted_status']['user']['followers_count']
        rt_count = tweet['retweeted_status']['retweet_count']
        tweet_text = tweet['retweeted_status']['full_text']
        user = tweet['retweeted_status']['user']['screen_name']
        id = tweet['retweeted_status']['id']
        verified = tweet['user']['verified']

    else:
        followers_count = tweet['user']['followers_count']
        rt_count = tweet['retweet_count']
        tweet_text = tweet['full_text']
        user = tweet['user']['screen_name']
        id = tweet['id']
        verified = tweet['user']['verified']


    if id not in previously_quoted_tweet_ids:

        if mentions_bang(tweet) == True:
            try:
                #Check that tweets has more than 100 RTs
                if  rt_count > 100 and tweet_counter ==0:
                    #Retweet the tweet!
                    but_with_a = (re.search('(?<=not with a bang)[\s\S]*', tweet_text, re.IGNORECASE)).group()
                    but_with_a = but_with_a.replace('\n', '').lower()
                    but_with_a = re.sub(r'http\S+', '', but_with_a)
                    but_with_a = re.sub(r'[\'"”.,]','',but_with_a)
                    but_with_a = re.sub(r'^ ', '', but_with_a )
                    if len(but_with_a) > 164:
                        but_with_a = but_with_a[:161] + "..."

                    tweet_url = f'https://twitter.com/{user}/status/{id}'
                    new_tweet= f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}\n\n{tweet_url}'
                    print(new_tweet)
                    twitter_bot.update_status(status=new_tweet)
                    tweet_counter +=1
                    print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
                #Check that Twitter account has more than 1000 followers
                elif followers_count > 5000 or verified == True and tweet_counter ==0:
                    #Retweet the tweet!
                    but_with_a = (re.search('(?<=not with a bang)[\s\S]*', tweet_text, re.IGNORECASE)).group()
                    but_with_a = but_with_a.replace('\n', '').lower()
                    but_with_a = re.sub(r'http\S+', '', but_with_a)
                    but_with_a = re.sub(r'[\'"”.,]','',but_with_a)
                    but_with_a = re.sub(r'^ ', '', but_with_a )
                    if len(but_with_a) > 164:
                        but_with_a = but_with_a[:161] + "..."

                    tweet_url = f'https://twitter.com/{user}/status/{id}'
                    new_tweet= f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}\n{tweet_url}'

                    twitter_bot.update_status(status=new_tweet)
                    print(new_tweet)
                    tweet_counter +=1
                    print(f"✨Met follower threshold✨ Succesfully retweeted {tweet_text}!")
            except TwythonError as e:
                print(e)
                print(f"ERROR! \n Tweet: {new_tweet} {tweet_text} \n Followers: {followers_count} \n URL: {tweet_url} \n RT:{rt_count}")
                continue

for tweet in mixed_results["statuses"]:

    if 'retweeted_status' in tweet.keys():
        followers_count = tweet['retweeted_status']['user']['followers_count']
        rt_count = tweet['retweeted_status']['retweet_count']
        tweet_text = tweet['retweeted_status']['full_text']
        user = tweet['retweeted_status']['user']['screen_name']
        id = tweet['retweeted_status']['id']
        verified = tweet['user']['verified']

    else:
        followers_count = tweet['user']['followers_count']
        rt_count = tweet['retweet_count']
        tweet_text = tweet['full_text']
        user = tweet['user']['screen_name']
        id = tweet['id']
        verified = tweet['user']['verified']

    if id not in previously_quoted_tweet_ids:

        if mentions_bang(tweet) == True:
            try:
                #Check that tweets has more than 100 RTs
                if  rt_count > 100 and tweet_counter ==0:
                    #Retweet the tweet!
                    but_with_a = (re.search('(?<=not with a bang)[\s\S]*', tweet_text, re.IGNORECASE)).group()
                    but_with_a = but_with_a.replace('\n', '').lower()
                    but_with_a = re.sub(r'http\S+', '', but_with_a)
                    but_with_a = re.sub(r'[\'"”.,]','',but_with_a)
                    but_with_a = re.sub(r'^ ', '', but_with_a )
                    if len(but_with_a) > 164:
                        but_with_a = but_with_a[:161] + "..."

                    tweet_url = f'https://twitter.com/{user}/status/{id}'
                    new_tweet= f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}\n{tweet_url}'
                    print(new_tweet)
                    twitter_bot.update_status(status=new_tweet)
                    tweet_counter +=1
                    print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
                #Check that Twitter account has more than 1000 followers
                elif followers_count > 5000 or verified == True and tweet_counter == 0:
                    #Retweet the tweet!
                    but_with_a = (re.search('(?<=not with a bang)[\s\S]*', tweet_text, re.IGNORECASE)).group()
                    but_with_a = but_with_a.replace('\n', '').lower()
                    but_with_a = re.sub(r'http\S+', '', but_with_a)
                    but_with_a = re.sub(r'[\'"”.,]','',but_with_a)
                    but_with_a = re.sub(r'^ ', '', but_with_a )
                    if len(but_with_a) > 164:
                        but_with_a = but_with_a[:161] + "..."

                    tweet_url = f'https://twitter.com/{user}/status/{id}'
                    new_tweet= f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}\n{tweet_url}'

                    twitter_bot.update_status(status=new_tweet)
                    print(new_tweet)
                    tweet_counter +=1
                    print(f"✨Met follower threshold✨ Succesfully retweeted {tweet_text}!")
            except TwythonError as e:
                print(e)
                print(f"ERROR! \n Tweet: {new_tweet} {tweet_text} \n Followers: {followers_count} \n URL: {tweet_url} \n RT:{rt_count}")
                continue

for tweet in recent_results["statuses"]:

    if 'retweeted_status' in tweet.keys():
        followers_count = tweet['retweeted_status']['user']['followers_count']
        rt_count = tweet['retweeted_status']['retweet_count']
        tweet_text = tweet['retweeted_status']['full_text']
        user = tweet['retweeted_status']['user']['screen_name']
        id = tweet['retweeted_status']['id']
        verified = tweet['user']['verified']
    else:
        followers_count = tweet['user']['followers_count']
        rt_count = tweet['retweet_count']
        tweet_text = tweet['full_text']
        user = tweet['user']['screen_name']
        id = tweet['id']
        verified = tweet['user']['verified']

    if id not in previously_quoted_tweet_ids:

        if mentions_bang(tweet) == True:
            try:
                #Check that tweets has more than 100 RTs
                if  rt_count > 100 and tweet_counter ==0:
                    #Retweet the tweet!
                    but_with_a = (re.search('(?<=not with a bang)[\s\S]*', tweet_text, re.IGNORECASE)).group()
                    but_with_a = but_with_a.replace('\n', '').lower()
                    but_with_a = re.sub(r'http\S+', '', but_with_a)
                    but_with_a = re.sub(r'[\'"”.,]','',but_with_a)
                    but_with_a = re.sub(r'^ ', '', but_with_a )
                    if len(but_with_a) > 164:
                        but_with_a = but_with_a[:161] + "..."

                    tweet_url = f'https://twitter.com/{user}/status/{id}'
                    new_tweet= f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}\n{tweet_url}'
                    print(new_tweet)
                    twitter_bot.update_status(status=new_tweet)
                    tweet_counter +=1
                    print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
                #Check that Twitter account has more than 1000 followers
                elif followers_count > 5000 or verified == True and tweet_counter ==0:
                    #Retweet the tweet!
                    but_with_a = (re.search('(?<=not with a bang)[\s\S]*', tweet_text, re.IGNORECASE)).group()
                    but_with_a = but_with_a.replace('\n', '').lower()
                    but_with_a = re.sub(r'http\S+', '', but_with_a)
                    but_with_a = re.sub(r'[\'"”.,]','',but_with_a)
                    but_with_a = re.sub(r'^ ', '', but_with_a )
                    if len(but_with_a) > 164:
                        but_with_a = but_with_a[:164]
                    print(len(but_with_a))

                    tweet_url = f'https://twitter.com/{user}/status/{id}'
                    new_tweet= f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}\n{tweet_url}'

                    twitter_bot.update_status(status=new_tweet)
                    print(new_tweet)
                    tweet_counter +=1
                    print(f"✨Met follower threshold✨ Succesfully retweeted {tweet_text}!")
            except TwythonError as e:
                print(e)
                print(f"ERROR! \n Tweet: {new_tweet} {tweet_text} \n Followers: {followers_count} \n URL: {tweet_url} \n RT:{rt_count}")
                continue
