from datetime import datetime
import json
import pandas as pd
import time
import tweepy

from db import init_db, insert_follower, query_follower_by_id, insert_dm_status, query_dm_status_by_id, \
    insert_skip_user, query_skip_user_by_id

from config import consumer_key, consumer_secret, access_token, access_token_secret, message, retry_message,\
    retry_after_days, filter_created_before, filter_min_followers_count, filter_min_friends_count, \
    filter_verified_only, test_flag, test_accounts, test_retry_message


def datetime_valid(dt_str):
    try:
        datetime.fromisoformat(dt_str)
    except Exception as e:
        return False
    return True


def get_total_follower_count():
    """
    Fetch total follower count
    :return: Total follower count
    """
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    me = api.me()
    return me._json['followers_count']


def build_filter_query():
    """ Build SQL query to filter follower information.
    :return: SQL query, SQL values
    """
    sql_str = "SELECT * FROM follower"
    sql_values = []

    if filter_created_before and datetime_valid(filter_created_before):

        if not sql_values:
            sql_str = sql_str + " WHERE created_at <= ?"
        else:
            sql_str = sql_str + " AND created_at <= ?"

        sql_values.append(filter_created_before)

    if filter_min_followers_count:

        if not sql_values:
            sql_str = sql_str + " WHERE followers_count >= ?"
        else:
            sql_str = sql_str + " AND followers_count >= ?"

        sql_values.append(filter_min_followers_count)

    if filter_min_friends_count:

        if not sql_values:
            sql_str = sql_str + " WHERE friends_count >= ?"
        else:
            sql_str = sql_str + " AND friends_count >= ?"

        sql_values.append(filter_min_friends_count)

    if not sql_values:
        sql_str = sql_str + " WHERE verified = ?"
    else:
        sql_str = sql_str + " AND verified = ?"

    sql_values.append(int(filter_verified_only))

    return sql_str, tuple(sql_values)


def process_user_info(conn, user_info_list):
    """ Process user information retrieved from twitter and store fields into db.
    :param conn: Connection object
    :param user_info_list: User information list retrieved from twitter
    :return: None
    """
    for i in range(len(user_info_list)):
        user_info = user_info_list[i]._json

        user_id = user_info['id']
        name = user_info['name']

        print(f"Process user information {name}")

        created_at = \
            datetime.strftime(datetime.strptime(user_info['created_at'],
                                                '%a %b %d %H:%M:%S +0000 %Y'),
                              '%Y-%m-%d %H:%M:%S')
        description = user_info['description']
        followers_count = user_info['followers_count']
        friends_count = user_info['friends_count']
        verified = user_info['verified']

        user = (user_id, name, created_at, description,
                followers_count, friends_count, verified)
        insert_follower(conn, user)


def process_test_user_info(user_info_list):
    """ Process test user information retrieved from twitter.
    :param user_info_list: User information list retrieved from twitter
    :return: Processed user information list
    """
    processed_user_info = []

    for i in range(len(user_info_list)):
        user_info = user_info_list[i]._json

        user_id = user_info['id']
        name = user_info['name']

        print(f"Process test user information {name}")

        created_at = \
            datetime.strftime(datetime.strptime(user_info['created_at'],
                                                '%a %b %d %H:%M:%S +0000 %Y'),
                              '%Y-%m-%d %H:%M:%S')
        description = user_info['description']
        followers_count = user_info['followers_count']
        friends_count = user_info['friends_count']
        verified = user_info['verified']

        user = (user_id, name, created_at, description,
                followers_count, friends_count, verified)
        processed_user_info.append(user)

    return processed_user_info


def send_dm(api, conn, user_info_list):
    """ Send DM to followers. Also support sending retry message if retry after limit is reached.
    :param api: Tweepy api object
    :param conn: Connection object
    :param user_info_list: Processed user information list
    :return: None
    """

    if test_flag:
        for i in range(len(user_info_list)):

            follower_id = user_info_list[i][0]
            follower_name = user_info_list[i][1]

            print(f"Sending DM to {follower_name}.")

            if not test_retry_message:
                dm = f"Hi {follower_name},\n" + message
            else:
                dm = f"Hi {follower_name},\n" + retry_message

            try:
                api.send_direct_message(follower_id, dm)

            except tweepy.RateLimitError as e:
                print(f"Info: Tweepy rate exceeded {str(e)}. Sleeping for 15 minutes.")
                time.sleep(60 * 15)
                return
            except tweepy.TweepError as e:
                print(f"Error: Tweepy error {str(e)}.")
                continue

    else:

        for i in range(len(user_info_list)):

            follower_id = user_info_list[i][0]
            follower_name = user_info_list[i][1]

            print(f"Sending DM to {follower_name}.")

            follower_dm_status = query_dm_status_by_id(conn, follower_id)

            if len(follower_dm_status) > 1:
                print(f"DM sent to {follower_name} twice already.")
                continue

            if len(follower_dm_status) == 1:
                dm = f"Hi {follower_name},\n" + retry_message
            else:
                dm = f"Hi {follower_name},\n" + message

            try:
                api.send_direct_message(follower_id, dm)

                current_time = str(datetime.now())[:-3]
                follower = (follower_id, current_time)
                insert_dm_status(conn, follower)

            except tweepy.RateLimitError as e:
                print(f"Info: Tweepy rate exceeded {str(e)}. Sleeping for 15 minutes.")
                time.sleep(60 * 15)
                return
            except tweepy.TweepError as e:
                print(f"Error: Tweepy error {str(e)}.")
                error_code = e.args[0][0]['code']

                # You cannot send messages to this user.
                if error_code == 349:
                    current_time = str(datetime.now())[:-3]
                    skip_user = (follower_id, current_time)
                    insert_skip_user(conn, skip_user)
                    continue

                return


def trigger_follower_processing():
    """ Start processing twitter follower data.
    :return: None
    """
    print(f"Triggering follower processing")

    # test accound limit
    max_test_account = 5

    # DM limit currently set by twitter
    dm_limit = 1000

    # initialize db
    conn = init_db()

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)

    me = api.me()
    total_followers_count = me._json['followers_count']

    # fetching follower ids
    follower_id_list = []
    if test_flag:
        print("Test flag is on. Check follower screen names from test accounts.")

        if len(test_accounts) == 0:
            print("Error: No test_accounts configured. Please add valid twitter screen names.")
            return

    else:
        print("Fetching follower list from twitter.")
        follower_id_cursor = tweepy.Cursor(api.followers_ids).items()
        while True:
            try:
                follower_id = follower_id_cursor.next()
                follower_info = query_follower_by_id(conn, follower_id)

                if follower_info is None:

                    # check if follower is present in skip user table
                    skip_user_info = query_skip_user_by_id(conn, follower_id)
                    if not skip_user_info:
                        follower_id_list.append(follower_id)

                    new_followers_count = len(follower_id_list)

                    # Fetch only needed amount of new follower ids
                    # Assuming filtering shall clear few users so limit is set to dm_limit*2
                    if (new_followers_count >= total_followers_count
                            or new_followers_count >= dm_limit*2):
                        break
                else:
                    follower_dm_status = query_dm_status_by_id(conn, follower_id)

                    if len(follower_dm_status) == 1:
                        # check for dm timestamp and see retry message can be sent
                        dm_status_timestamp = pd.to_datetime(follower_dm_status[0][1])
                        current_timestamp = datetime.now()

                        time_difference = current_timestamp - dm_status_timestamp
                        if time_difference.days > retry_after_days:
                            follower_id_list.append(follower_id)

            except tweepy.RateLimitError as e:
                print(f"Info: Tweepy rate exceeded {str(e)}. Sleeping for 15 minutes.")
                time.sleep(60 * 15)
                continue
            except tweepy.TweepError as e:
                print(f"Error: Tweepy error {str(e)}.")
                return
            except StopIteration:
                break

    # fetch user information from twitter and store it on DB.
    if follower_id_list:
        print("Fetching follower details from twitter.")
        lookup_users_count = 100

        iterations = total_followers_count // lookup_users_count
        if total_followers_count % lookup_users_count:
            iterations = iterations + 1

        for i in range(iterations):

            start_index = i * lookup_users_count
            if i == iterations-1:
                end_index = None
            else:
                end_index = (i+1) * lookup_users_count

            user_id_list = follower_id_list[start_index:end_index]

            try:
                user_info_list = api.lookup_users(user_id_list)
                process_user_info(conn, user_info_list)
            except tweepy.RateLimitError as e:
                print(f"Info: Tweepy rate exceeded {str(e)}. Sleeping for 15 minutes.")
                time.sleep(60 * 15)
                break
            except tweepy.TweepError as e:
                print(f"Error: Tweepy error {str(e)}.")
                return
    else:
        print("No new follower information.")

    # filter and send DMs
    if test_flag:
        print("Sending DMs for configured test accounts.")

        try:
            # support only lookup for max_test_account
            print(test_accounts[:max_test_account])
            user_info_list = api.lookup_users(screen_names=test_accounts[:max_test_account])

            processed_user_info_list = process_test_user_info(user_info_list)
            send_dm(api, conn, processed_user_info_list)

        except tweepy.RateLimitError as e:
            print(f"Info: Tweepy rate exceeded {str(e)}. Sleeping for 15 minutes.")
            time.sleep(60 * 15)
        except tweepy.TweepError as e:
            print(f"Error: Tweepy error {str(e)}.")
            return

    else:
        # filter users from db based on filters
        built_query = build_filter_query()

        cur = conn.cursor()
        cur.execute(built_query[0], built_query[1])

        shortlisted_followers = cur.fetchall()

        # sending DM to shortlisted followers
        # send_dm(api, conn, shortlisted_followers)  # to be uncommented
