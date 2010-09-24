import tweepy

TWITTER_KEY = 'tKsHRNjBo8QErGrjyDkGg'
TWITTER_SECRET = 'nCbFAzd21T3LluTYAk9XAuVt1IPMa6yoB5x74ymEA8'
MY_KEY = '194555494-5RLSPDPg9sid0kJzUOzo22W9wDwoRIqHaweyIgWc'
MY_SECRET = '4tzsO3MTH9eSvOY7pZwXySa0YGtUTKuShjorprFQc'

auth = tweepy.OAuthHandler(TWITTER_KEY, TWITTER_SECRET)
auth.set_access_token(MY_KEY, MY_SECRET)
api = tweepy.API(auth)

