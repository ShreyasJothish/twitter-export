import json


with open('config.json') as config_file:
    config_data = json.load(config_file)

print("Loading twitter configurations.")
consumer_key = config_data['twitter']['consumer_key']
consumer_secret = config_data['twitter']['consumer_secret']
access_token = config_data['twitter']['access_token']
access_token_secret = config_data['twitter']['access_token_secret']

print("Loading db file path")
db_file = config_data['db_file']

print("Loading DM messages.")
enable_dm_flag = config_data['enable_dm_flag']
message = config_data['message']
retry_message = config_data['retry_message']
retry_after_days = config_data['retry_after_days']

print("Loading filters for followers.")
filter_created_before = config_data['follower_filters']['created_before']
filter_min_followers_count = config_data['follower_filters']['min_followers_count']
filter_max_followers_count = config_data['follower_filters']['max_followers_count']
filter_min_friends_count = config_data['follower_filters']['min_friends_count']
filter_max_friends_count = config_data['follower_filters']['max_friends_count']
filter_verified_only = config_data['follower_filters']['verified_only']

print("Loading test configurations.")
test_flag = config_data['test_flag']
test_accounts = config_data['test_accounts']
test_retry_message =  config_data['test_retry_message']
