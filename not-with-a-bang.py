# -*- coding: utf-8 -*-

from twython import Twython, TwythonError
from secrets import *
import regex as re
from twarc import Twarc2, expansions
import datetime
import json
import sys

from inspect import currentframe, getframeinfo


#Initialize Twitter bot
twitter_bot = Twython(app_key, app_secret, oauth_token, oauth_token_secret)

# Replace your bearer token below
client = Twarc2(bearer_token=bearer_token)

# Specify the start time in UTC for the time period you want Tweets from
start_time = datetime.datetime(2009, 1, 1, 0, 0, 0, 0, datetime.timezone.utc)

# Specify the end time in UTC for the time period you want Tweets from
#end_time = datetime.datetime(2021, 5, 30, 0, 0, 0, 0, datetime.timezone.utc)


# The search_all method call the full-archive search endpoint to get Tweets based on the query, start and end times
recent_search_results = client.search_recent(query="(\"not with a bang\") OR (\"This is the way\" \"not with a\" \"but\") OR (\"This is how\" \"not with a\" \"but\")", max_results=100)


#Tweet counter to make sure that the bot only retweets one tweet every time the script runs
tweet_counter=0

#Look up previously tweeted IDs
#previously_quoted_tweet_ids = [tweet['quoted_status_id'] for tweet in twitter_bot.get_home_timeline()]
#Look up previously tweeted IDs
timeline_tweets = client.timeline("notwithabangbut")
previously_quoted_tweet_ids = []
for page in timeline_tweets:
    result = expansions.flatten(page)
    for tweet in result:
        if 'referenced_tweets' in tweet.keys():
            referenced_tweets = tweet['referenced_tweets']
            for referenced_tweet in referenced_tweets:
                #print(referenced_tweet['id'])
                previously_quoted_tweet_ids.append(referenced_tweet['id'])

previously_quoted_tweet_ids.append('758015741039931392')

def mentions_ends(status):
    # Remove capital letters and excessive whitespace/linebreaks
    test_text = ' '.join(status.lower().split())
    test_text = re.sub(r'[^\w\s]','',test_text)

    if 'this is the way' in test_text or 'this is how' in test_text and 'not with' in test_text and 'world' not in test_text and 'comb over' not in test_text:
        return True
    else:
        return False

def mentions_bang(status):
    # Remove capital letters and excessive whitespace/linebreaks
    test_text = ' '.join(status.lower().split())
    test_text = re.sub(r'[^\w\s]','',test_text)

    if 'bang' in test_text and 'comb over' not in test_text and 'whimper' not in test_text:
        return True
    else:
        return False

def format_bang_followup(tweet_text):
    tweet_text = tweet_text.replace('\n', ' ')
    # Capture after "not with a bang" and before a period or hashtag
    if (re.search('(?<=not with a bang).*?(?=\.\s|#|"|”)', tweet_text, re.IGNORECASE)) != None:
        but_with_a = (re.search('(?<=not with a bang).*?(?=\.\s|#|"|”)', tweet_text, re.IGNORECASE)).group()
    elif (re.search('(?<=not with a bang).*', tweet_text, re.IGNORECASE)) != None:
        but_with_a = (re.search('(?<=not with a bang).*', tweet_text, re.IGNORECASE)).group()
    else:
        but_with_a = "but a whimper"
    # Replace line breaks with a space
    but_with_a = re.sub(r'http\S+', '', but_with_a)
    #but_with_a = re.sub(r'[\'"”.,]','',but_with_a)
    but_with_a = re.sub(r'^[,]','',but_with_a)
    but_with_a = re.sub(r'[\'"”.!:;?]$','',but_with_a)
    but_with_a = re.sub(r'^ ', '', but_with_a )
    # Strip duplicate white space
    but_with_a =  re.sub(' +', ' ', but_with_a)
    #but_with_a = (but_with_a[:161] + "...") if len(but_with_a) > 164 else but_with_a
    but_with_a = (but_with_a[:161] + "...") if len(but_with_a) > 164 else but_with_a
    but_with_a = but_with_a.strip()
    return but_with_a

def format_the_blank_followup(tweet_text):
    # Capture after "This is the way" or "This is how" and before "not with a"
    the_blank = (re.search('(?<=This is the way|<=This is how).*?(?=not with|\n*not with|.not with)', tweet_text, re.IGNORECASE)).group()
    the_blank = the_blank.replace('\n', ' ')
    the_blank = re.sub(r'http\S+', '', the_blank)
    the_blank = re.sub(r'[\'"”.:;,]','', the_blank)
    the_blank = re.sub(r'^ ', '', the_blank)
    the_blank = the_blank.strip()
    return the_blank



# https://stackoverflow.com/questions/56873367/how-to-make-text-bold-or-italic-while-posting-a-tweet-to-the-twitter-account-fro
def make_italics(input_text):

    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    bold_chars = "𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻0123456789"

    output = ""

    for character in input_text:
        if character in chars:
            output += bold_chars[chars.index(character)]
        else:
            output += character

    return output


for page in recent_search_results:
    result = expansions.flatten(page)
    for tweet in result:

        if 'referenced_tweets' in tweet.keys():
            referenced_tweets = tweet['referenced_tweets']
            for referenced_tweet in referenced_tweets:
            #print(tweet)
                if 'author' in referenced_tweet.keys():
                    followers_count = referenced_tweet['author']['public_metrics']['followers_count']
                    rt_count = referenced_tweet['public_metrics']['retweet_count']
                    tweet_text = referenced_tweet['text']
                    user = referenced_tweet['author']['username']
                    indy_user = tweet['author']['username']
                    retweet_id = referenced_tweet['id']
                    tweet_id = tweet['id']
                    verified = referenced_tweet['author']['verified']

                    if str(retweet_id) not in previously_quoted_tweet_ids and str(tweet_id) not in previously_quoted_tweet_ids:

                        if mentions_bang(tweet_text) == True and mentions_ends(tweet_text) == True:
                            try:
                                if tweet_counter == 0:
                                #Check that tweets has more than 100 RTs
                                    if  rt_count > 100:
                                        #Retweet the tweet!
                                        but_with_a = format_bang_followup(tweet_text)

                                        if (re.search('(?<=This is the way|<=This is how).*?(?=not with|\n*not with|.not with)', tweet_text, re.IGNORECASE)) != None:
                                            the_blank = format_the_blank_followup(tweet_text)
                                        else:
                                            the_blank = "the world ends"
                                        tweet_url = f'https://twitter.com/{user}/status/{retweet_id}'
                                        new_tweet= f'This is the way {the_blank}\nThis is the way {the_blank}\nNot with {but_with_a}.'
                                        new_tweet = twitter_bot.update_status(status=new_tweet)
                                        reply_tweet = twitter_bot.update_status(status=f"\n\n{tweet_url}", in_reply_to_status_id=new_tweet['id'], auto_populate_reply_metadata=True)
                                        #new_tweet= f'This is the way {the_blank}\nThis is the way {the_blank}\nNot with a bang {but_with_a}.' + f"\n\n{tweet_url}"

                                        tweet_counter +=1
                                        print(f"Supposed retweet \n Retweet user: {user} \n Tweet user : {indy_user} \n Retweet id: {retweet_id} \n Tweet id: {tweet_id}")
                                        print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
                                        frameinfo = getframeinfo(currentframe())
                                        print(frameinfo.filename, frameinfo.lineno)

                                        but_with_a = format_bang_followup(tweet_text)

                                        if (re.search('(?<=This is the way|<=This is how).*?(?=not with a|\n*not with a|.not with a)', tweet_text, re.IGNORECASE)) != None:
                                            the_blank = format_the_blank_followup(tweet_text)
                                        else:
                                            the_blank = "the world ends"
                                        tweet_url = f'https://twitter.com/{user}/status/{retweet_id}'
                                        new_tweet= f'This is the way {the_blank}\nThis is the way {the_blank}\nNot with {but_with_a}.'
                                        new_tweet = twitter_bot.update_status(status=new_tweet)
                                        reply_tweet = twitter_bot.update_status(status=f"\n\n{tweet_url}", in_reply_to_status_id=new_tweet['id'], auto_populate_reply_metadata=True)
                                        #new_tweet= f'This is the way {the_blank}\nThis is the way {the_blank}\nNot with a bang {but_with_a}.' + f"\n\n{tweet_url}"

                                        tweet_counter +=1
                                        print(f"Supposed retweet \n Retweet user: {user} \n Tweet user : {indy_user} \n Retweet id: {retweet_id} \n Tweet id: {tweet_id}")
                                        print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
                                        frameinfo = getframeinfo(currentframe())
                                        print(frameinfo.filename, frameinfo.lineno)
                                else:
                                    print("Done tweeting")
                                    sys.exit(1)
                            except TwythonError as e:
                                print(e)
                                print(f"ERROR! \n Tweet: {new_tweet} {tweet_text} \n Followers: {followers_count} \n URL: {tweet_url} \n RT:{rt_count}")
                                print(f"Supposed retweet \n Retweet user: {user} \n Tweet user : {indy_user} \n Retweet id: {retweet_id} \n Tweet id: {tweet_id}")
                                continue

                        elif mentions_bang(tweet_text) == True:
                            try:
                                if tweet_counter == 0:
                                #Check that tweets has more than 100 RTs
                                    if  rt_count > 100 :
                                        #Retweet the tweet!
                                        but_with_a = format_bang_followup(tweet_text)

                                        tweet_url = f'https://twitter.com/{user}/status/{retweet_id}'
                                        new_tweet = f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}.'
                                        new_tweet = twitter_bot.update_status(status=new_tweet)

                                        #new_tweet= f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}.' + f"\n\n{tweet_url}"
                                        reply_tweet = twitter_bot.update_status(status=f"\n\n{tweet_url}", in_reply_to_status_id=new_tweet['id'], auto_populate_reply_metadata=True)

                                        tweet_counter +=1
                                        print(f"Supposed retweet \n Retweet user: {user} \n Tweet user : {indy_user} \n Retweet id: {retweet_id} \n Tweet id: {tweet_id}")
                                        print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
                                        frameinfo = getframeinfo(currentframe())
                                        print(frameinfo.filename, frameinfo.lineno)
                                    elif followers_count > 5000 or verified == True:
                                            #Retweet the tweet!
                                            but_with_a = format_bang_followup(tweet_text)

                                            tweet_url = f'https://twitter.com/{user}/status/{retweet_id}'
                                            new_tweet = f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}.'
                                            new_tweet = twitter_bot.update_status(status=new_tweet)

                                            #new_tweet= f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}.' + f"\n\n{tweet_url}"
                                            reply_tweet = twitter_bot.update_status(status=f"\n\n{tweet_url}", in_reply_to_status_id=new_tweet['id'], auto_populate_reply_metadata=True)

                                            tweet_counter +=1
                                            print(f"Supposed retweet \n Retweet user: {user} \n Tweet user : {indy_user} \n Retweet id: {retweet_id} \n Tweet id: {tweet_id}")
                                            print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
                                            frameinfo = getframeinfo(currentframe())
                                            print(frameinfo.filename, frameinfo.lineno)

                                else:
                                    print("Done tweeting")
                                    sys.exit(1)
                            except TwythonError as e:
                                print(e)
                                print(f"ERROR! \n Tweet: {new_tweet} {tweet_text} \n Followers: {followers_count} \n URL: {tweet_url} \n RT:{rt_count}")
                                print(f"Supposed retweet \n Retweet user: {user} \n Tweet user : {indy_user} \n Retweet id: {retweet_id} \n Tweet id: {tweet_id}")
                                continue
                        elif mentions_ends(tweet_text) == True:
                            try:
                                if tweet_counter == 0:
                                #Check that tweets has more than 100 RTs
                                    if  rt_count > 100:
                                        #Retweet the tweet!
                                        if (re.search('(?<=This is the way|<=This is how).*?(?=not with|\n*not with|.not with)', tweet_text, re.IGNORECASE)) != None:
                                            the_blank = format_the_blank_followup(tweet_text)
                                        else:
                                            the_blank = "the world ends"

                                        tweet_url = f'https://twitter.com/{user}/status/{retweet_id}'
                                        new_tweet = f'This is the way {the_blank}\nThis is the way {the_blank}\nNot with a bang but a whimper.'
                                        #new_tweet= f'This is the way {the_blank}\nThis is the way {the_blank}\nNot with a bang {but_with_a}.' + f"\n\n{tweet_url}"
                                        new_tweet = twitter_bot.update_status(status=new_tweet)

                                        reply_tweet = twitter_bot.update_status(status=f"\n\n{tweet_url}", in_reply_to_status_id=new_tweet['id'], auto_populate_reply_metadata=True)

                                        tweet_counter +=1
                                        print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
                                        frameinfo = getframeinfo(currentframe())
                                        print(frameinfo.filename, frameinfo.lineno)
                                    elif followers_count > 5000 or verified == True:
                                            #Retweet the tweet!
                                            if (re.search('(?<=This is the way|<=This is how).*?(?=not with a|\n*not with a|.not with a)', tweet_text, re.IGNORECASE)) != None:
                                                the_blank = format_the_blank_followup(tweet_text)
                                            else:
                                                the_blank = "the world ends"

                                            tweet_url = f'https://twitter.com/{user}/status/{retweet_id}'
                                            new_tweet = f'This is the way {the_blank}\nThis is the way {the_blank}\nNot with a bang but a whimper.'
                                            #new_tweet= f'This is the way {the_blank}\nThis is the way {the_blank}\nNot with a bang {but_with_a}.' + f"\n\n{tweet_url}"
                                            new_tweet = twitter_bot.update_status(status=new_tweet)

                                            reply_tweet = twitter_bot.update_status(status=f"\n\n{tweet_url}", in_reply_to_status_id=new_tweet['id'], auto_populate_reply_metadata=True)

                                            tweet_counter +=1
                                            print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
                                            frameinfo = getframeinfo(currentframe())
                                            print(frameinfo.filename, frameinfo.lineno)
                                else:
                                    print("Done tweeting")
                                    sys.exit(1)
                            except TwythonError as e:
                                print(e)
                                print(f"ERROR! \n Tweet: {new_tweet} {tweet_text} \n Followers: {followers_count} \n URL: {tweet_url} \n RT:{rt_count}")
                                print(f"Supposed retweet \n Retweet user: {user} \n Tweet user : {indy_user} \n Retweet id: {retweet_id} \n Tweet id: {tweet_id}")
                                continue

search_results = client.search_all(query="(\"not with a bang\") OR (\"This is the way\" \"not with a bang\") OR (\"This is how\" \"not with a bang\")", start_time=start_time, max_results=100)

for page in search_results:
    result = expansions.flatten(page)
    for tweet in result:

        if 'referenced_tweets' in tweet.keys():
            referenced_tweets = tweet['referenced_tweets']
            for referenced_tweet in referenced_tweets:
            #print(tweet)
                if 'author' in referenced_tweet.keys():
                    followers_count = referenced_tweet['author']['public_metrics']['followers_count']
                    rt_count = referenced_tweet['public_metrics']['retweet_count']
                    tweet_text = referenced_tweet['text']
                    user = referenced_tweet['author']['username']
                    indy_user = tweet['author']['username']
                    retweet_id = referenced_tweet['id']
                    tweet_id = tweet['id']
                    verified = referenced_tweet['author']['verified']

                    if str(retweet_id) not in previously_quoted_tweet_ids and str(tweet_id) not in previously_quoted_tweet_ids:

                        if mentions_bang(tweet_text) == True and mentions_ends(tweet_text) == True:
                            try:
                                if tweet_counter == 0:
                                #Check that tweets has more than 100 RTs
                                    if  rt_count > 100 or followers_count > 5000 or verified == True:
                                        #Retweet the tweet!
                                        but_with_a = format_bang_followup(tweet_text)

                                        if (re.search('(?<=This is the way|<=This is how).*?(?=not with a|\n*not with a|.not with a)', tweet_text, re.IGNORECASE)) != None:
                                            the_blank = format_the_blank_followup(tweet_text)
                                        else:
                                            the_blank = "the world ends"
                                        tweet_url = f'https://twitter.com/{user}/status/{retweet_id}'
                                        new_tweet= f'This is the way {the_blank}\nThis is the way {the_blank}\nNot with a bang {but_with_a}.'
                                        new_tweet = twitter_bot.update_status(status=new_tweet)
                                        reply_tweet = twitter_bot.update_status(status=f"\n\n{tweet_url}", in_reply_to_status_id=new_tweet['id'], auto_populate_reply_metadata=True)
                                        #new_tweet= f'This is the way {the_blank}\nThis is the way {the_blank}\nNot with a bang {but_with_a}.' + f"\n\n{tweet_url}"

                                        tweet_counter +=1
                                        print(f"Supposed retweet All Search Results \n Retweet user: {user} \n Tweet user : {indy_user} \n Retweet id: {retweet_id} \n Tweet id: {tweet_id}")
                                        print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
                                        frameinfo = getframeinfo(currentframe())
                                        print(frameinfo.filename, frameinfo.lineno)

                                else:
                                    print("Done tweeting")
                                    sys.exit(1)
                            except TwythonError as e:
                                print(e)
                                print(f"ERROR! \n Tweet: {new_tweet} {tweet_text} \n Followers: {followers_count} \n URL: {tweet_url} \n RT:{rt_count}")
                                print(f"Supposed retweet \n Retweet user: {user} \n Tweet user : {indy_user} \n Retweet id: {retweet_id} \n Tweet id: {tweet_id}")
                                continue

                        elif mentions_bang(tweet_text) == True:
                            try:
                                if tweet_counter == 0:
                                #Check that tweets has more than 100 RTs
                                    if  rt_count > 100 or followers_count > 5000 or verified == True:
                                        #Retweet the tweet!
                                        but_with_a = format_bang_followup(tweet_text)

                                        tweet_url = f'https://twitter.com/{user}/status/{retweet_id}'
                                        new_tweet = f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}.'
                                        new_tweet = twitter_bot.update_status(status=new_tweet)

                                        #new_tweet= f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}.' + f"\n\n{tweet_url}"
                                        reply_tweet = twitter_bot.update_status(status=f"\n\n{tweet_url}", in_reply_to_status_id=new_tweet['id'], auto_populate_reply_metadata=True)

                                        tweet_counter +=1
                                        print(f"Supposed retweet \n Retweet user: {user} \n Tweet user : {indy_user} \n Retweet id: {retweet_id} \n Tweet id: {tweet_id}")
                                        print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
                                        frameinfo = getframeinfo(currentframe())
                                        print(frameinfo.filename, frameinfo.lineno)
                                else:
                                    print("Done tweeting")
                                    sys.exit(1)
                            except TwythonError as e:
                                print(e)
                                print(f"ERROR! \n Tweet: {new_tweet} {tweet_text} \n Followers: {followers_count} \n URL: {tweet_url} \n RT:{rt_count}")
                                print(f"Supposed retweet \n Retweet user: {user} \n Tweet user : {indy_user} \n Retweet id: {retweet_id} \n Tweet id: {tweet_id}")
                                continue
                        elif mentions_ends(tweet_text) == True:
                            try:
                                if tweet_counter == 0 or followers_count > 5000 or verified == True:
                                #Check that tweets has more than 100 RTs
                                    if  rt_count > 100:
                                        #Retweet the tweet!
                                        if (re.search('(?<=This is the way|<=This is how).*?(?=not with a|\n*not with a|.not with a)', tweet_text, re.IGNORECASE)) != None:
                                            the_blank = format_the_blank_followup(tweet_text)
                                        else:
                                            the_blank = "the world ends"

                                        tweet_url = f'https://twitter.com/{user}/status/{retweet_id}'
                                        new_tweet = f'This is the way {the_blank}\nThis is the way {the_blank}\nNot with a bang but a whimper.'
                                        #new_tweet= f'This is the way {the_blank}\nThis is the way {the_blank}\nNot with a bang {but_with_a}.' + f"\n\n{tweet_url}"
                                        new_tweet = twitter_bot.update_status(status=new_tweet)

                                        reply_tweet = twitter_bot.update_status(status=f"\n\n{tweet_url}", in_reply_to_status_id=new_tweet['id'], auto_populate_reply_metadata=True)

                                        tweet_counter +=1
                                        print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
                                        frameinfo = getframeinfo(currentframe())
                                        print(frameinfo.filename, frameinfo.lineno)
                                else:
                                    print("Done tweeting")
                                    sys.exit(1)
                            except TwythonError as e:
                                print(e)
                                print(f"ERROR! \n Tweet: {new_tweet} {tweet_text} \n Followers: {followers_count} \n URL: {tweet_url} \n RT:{rt_count}")
                                print(f"Supposed retweet \n Retweet user: {user} \n Tweet user : {indy_user} \n Retweet id: {retweet_id} \n Tweet id: {tweet_id}")
                                continue
    # else:
    #     followers_count = tweet['author']['public_metrics']['followers_count']
    #     rt_count = tweet['public_metrics']['retweet_count']
    #     tweet_text = tweet['text']
    #     user = tweet['author']['username']
    #     id = tweet['id']
    #     verified = tweet['author']['verified']
    #
    #     if str(id) not in previously_quoted_tweet_ids:
    #
    #         if mentions_bang(tweet_text) == True and mentions_ends(tweet_text) == True:
    #             try:
    #                 if tweet_counter == 0:
    #                 #Check that tweets has more than 100 RTs
    #                     if  rt_count > 100 or followers_count > 5000 or verified == True:
    #                         #Retweet the tweet!
    #                         but_with_a = format_bang_followup(tweet_text)
    #                         the_blank = format_the_blank_followup(tweet_text)
    #
    #
    #                         tweet_url = f'https://twitter.com/{user}/status/{id}'
    #                         new_tweet= make_italics(f'This is the way {the_blank} ends\nThis is the way {the_blank} ends\nNot with a bang {but_with_a}.') + f"\n{tweet_url}"
    #                         twitter_bot.update_status(status=new_tweet)
    #                         tweet_counter +=1
    #                         print(f"Supposed regular tweet \n Tweet user : {user} \n Tweet id: {id}")
    #                         print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
    #
    #                 else:
    #                     print("Done tweeting")
    #                     sys.exit(1)
    #             except TwythonError as e:
    #                 print(e)
    #                 print(f"ERROR! \n Tweet: {new_tweet} {tweet_text} \n Followers: {followers_count} \n URL: {tweet_url} \n RT:{rt_count}")
    #                 print(f"Supposed regular tweet \n Tweet user : {user} \n Tweet id: {id}")
    #                 continue
    #
    #         elif mentions_bang(tweet_text) == True:
    #             try:
    #                 if tweet_counter == 0:
    #                 #Check that tweets has more than 100 RTs
    #                     if  rt_count > 100 or followers_count > 5000 or verified == True:
    #                         #Retweet the tweet!
    #                         but_with_a = format_bang_followup(tweet_text)
    #
    #                         tweet_url = f'https://twitter.com/user/status/{id}'
    #                         new_tweet= make_italics(f'This is the way the world ends\nThis is the way the world ends\nNot with a bang {but_with_a}.') + f"\n{tweet_url}"
    #
    #                         twitter_bot.update_status(status=new_tweet)
    #                         tweet_counter +=1
    #                         print(f"Supposed regular tweet \n Tweet user : {user} \n Tweet id: {id}")
    #                         print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
    #                 else:
    #                     print("Done tweeting")
    #                     sys.exit(1)
    #             except TwythonError as e:
    #                 print(e)
    #                 print(f"ERROR! \n Tweet: {new_tweet} {tweet_text} \n Followers: {followers_count} \n URL: {tweet_url} \n RT:{rt_count}")
    #                 print(f"Supposed regular tweet \n Tweet user : {user} \n Tweet id: {id}")
    #
    #                 continue
    #
    #         elif mentions_ends(tweet_text) == True:
    #             try:
    #                 if tweet_counter == 0:
    #                 #Check that tweets has more than 100 RTs
    #                     if  rt_count > 100:
    #                         #Retweet the tweet!
    #                         the_blank = format_the_blank_followup(tweet_text)
    #
    #
    #                         tweet_url = f'https://twitter.com/{user}/status/{id}'
    #                         new_tweet= make_italics(f'This is the way {the_blank} ends\nThis is the way {the_blank} ends\nNot with a bang {but_with_a}.') + f"\n{tweet_url}"
    #
    #                         twitter_bot.update_status(status=new_tweet)
    #                         tweet_counter +=1
    #                         print(f"Supposed regular tweet \n Tweet user : {user} \n Tweet id: {id}")
    #                         print(f"✨Met RT threshold✨ Succesfully retweeted {tweet_text}!")
    #
    #                     #Check that Twitter account has more than 1000 followers
    #                     elif followers_count > 5000 or verified == True:
    #                         #Retweet the tweet!
    #                         the_blank = format_the_blank_followup(tweet_text)
    #
    #                         tweet_url = f'https://twitter.com/{user}/status/{id}'
    #                         new_tweet= make_italics(f'This is the way {the_blank} ends\nThis is the way {the_blank} ends\nNot with a bang {but_with_a}.') + f"\n{tweet_url}"
    #
    #                         twitter_bot.update_status(status=new_tweet)
    #
    #                         tweet_counter +=1
    #                         print(f"Supposed regular tweet \n Tweet user : {user} \n Tweet id: {id}")
    #                         print(f"✨Met follower threshold✨ Succesfully retweeted {tweet_text}!")
    #                 else:
    #                     print("Done tweeting")
    #                     sys.exit(1)
    #             except TwythonError as e:
    #                 print(e)
    #                 print(f"ERROR! \n Tweet: {new_tweet} {tweet_text} \n Followers: {followers_count} \n URL: {tweet_url} \n RT:{rt_count}")
    #                 print(f"Supposed regular tweet \n Tweet user : {user} \n Tweet id: {id}")
    #
    #                 continue
