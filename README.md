# Twitter Exporter
Twitter Exporter is designed to be a desktop application with single user in mind. However this solution can be scaled,
to cloud based solution with added security features like OAuth sign-in and higher performance database with minor 
code changes.

## Key Features
1. Security keys and follower data stored on locally on user's system and not shared outside.
2. Visualization of fetch subset of follower's information from twitter for analysis before sending DMs.
3. Multiple filter options to select followers to send DM with subscription links. 
Currently available filters:
    a) Filter followers based on their twitter joining date.
    b) Filter followers based on minimum number of their followers.
    c) Filter followers based on minimum number of their friends.
    d) Filter and categorize high value followers (power users) based on maximum number of their followers.
    e) Filter and categorize high value followers (power users) based on maximum number of their friends.
    f) Filter followers who are verified by twitter.
4. Provision to send DM and retry DM after configured number of days. Follower name will be auto filled in DM.
5. Test functionality to try DM and retry DM on up to 5 configured twitter accounts.
6. Visualize statistics on screen.
7. Hover over individual marker on plot to get details about specific follower.
8. Option to export data as csv.
    a) High value follower information currently fetched. 
    High value follower is identified based on their respective follower and friends count.
    b) Follower information currently fetched.
    c) DM status with timestamp mapped based on follower id.
    d) Skipped follower (followers for whom you do not have access to send DM) information currently fetched.
9. Automatic fetch and DM option based on twitter rate limit.
10. Auto refresh of visualization and summary.

## Development environment
Ubuntu 20.04 LTS running Python 3.8.2

## Set up
### Requirements
Python 3+

### Steps
1. Download source code.
2. Create and activate virtual environment. (Recommended)
    Refer `https://naysan.ca/2019/08/05/install-python-3-virtualenv-on-ubuntu/` and execute till Step 5:
3. Install dependent python packages.

    `pip install -r requirements.txt`
4. Check and update config.json. Refer to *Configuration* section.
5. Run application.

    `python app.py`
6. Access dash board at `http://127.0.0.1:8050/`
7. Press CTRL+C to exit.


## Configuration
### Description
```
*twitter* - Keys and tokens needed to access twitter apis are defined here.
To create and get the configuration details visit https://developer.twitter.com/
"twitter" : {
"consumer_key": API key under section "Consumer API keys".
"consumer_secret": API secret key under section "Consumer API keys".
"access_token": Access token under section "Access token & access token secret".
"access_token_secret":  Access token secret under section "Access token & access token secret".
}
Note: Ensure Access tokens have *Access level: Read, write, and Direct Messages*

"db_file": Sqlite database file name used for storing follower information.

"test_flag": Flag to control application setting.
    "true" - Application test settings. DMs shall be sent to test accounts.
    "false" - Application live settings. DMs shall be sent to followers.
"test_accounts": List of test user's twitter screen names.
"test_retry_message": Flag to test retry DM message.
    "true" - Use *retry_message* as DM.
    "false" - Use message as DM.

"enable_dm_flag": Flag controls sending of DMs to followers. To avoid accidental sending of DMs.
    "true" - Sending DMs to followers enabled.
    "false" - Sending DMs to followers disabled.
"message": DM used during 1st attempt.
"retry_message": DM used during 2nd attempt.
"retry_after_days": Number of days after which *retry_message* is attempted after 1st DM.

*follower_filters* - Filters which can be applied to followers on twitter are defined here.
"follower_filters": {
"created_before": ISO Format (%Y-%m-%d %H:%M:%S) date time to select followers based on joining date to twitter.
"min_followers_count": Select followers based on minimum follower count of the follower.
"max_followers_count": Select followers based on maximum follower count of the follower.
"min_friends_count": Select followers based on minimum friends count of the follower.
"max_friends_count": Select followers based on maximum friends count of the follower.
"verified_only": Select followers based on verified by twitter flag.
}
Note: Using *min* and *max* configurations, you can send different DMs to high value followers as compared to regular
followers. Currently you have to manage the DMs manually. Suggested to work backwards ie. have set of DMs for 
high value followers and once you have reached them move onto the next batch.
```

### Sample
```
{
  "twitter" : {
    "consumer_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "consumer_secret": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "access_token": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "access_token_secret": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
  },
  "db_file": "twitter_export.db",
  "test_flag": true,
  "test_accounts": ["balajis","ShreyasJothish"],
  "test_retry_message": false,
  "enable_dm_flag": false,
  "message": "subscription message and link",
  "retry_message": "retry subscription message and link",
  "retry_after_days": 7,
  "follower_filters": {
    "created_before": "2019-06-27 00:00:00",
    "min_followers_count": 100,
    "max_followers_count": 10000,
    "min_friends_count": 50,
    "max_friends_count": 10000,
    "verified_only": false
  }
}
```
