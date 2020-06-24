import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return: True is table is created successfully else False
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
        return False

    return True


def init_db(db_file):
    """ initialise sqllite db
    :param db_file: database file
    :return: Connection object or None
    """
    database = db_file

    sql_create_follower_table = """ CREATE TABLE IF NOT EXISTS follower (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        created_at text,
                                        description text,
                                        followers_count integer,
                                        friends_count integer,
                                        verified integer
                                    ); """

    sql_create_dm_status_table = """ CREATE TABLE IF NOT EXISTS dm_status (
                                    id integer,
                                    timestamp text
                                ); """

    sql_create_skip_user_table = """ CREATE TABLE IF NOT EXISTS skip_user (
                                    id integer,
                                    timestamp text
                                ); """

    # create a database connection
    conn = create_connection(database)

    if conn is None:
        print("Error! cannot create the database connection.")
        return

    # create tables
    # create followers table
    status = create_table(conn, sql_create_follower_table)
    if not status:
        print("Error! creation of followers table failed.")
        return

    # create dm status table
    status = create_table(conn, sql_create_dm_status_table)
    if not status:
        print("Error! creation of dm status table failed.")
        return

    # create skip user table
    status = create_table(conn, sql_create_skip_user_table)
    if not status:
        print("Error! creation of skip user table failed.")
        return

    return conn


def insert_follower(conn, follower):
    """
    Add a new follower into db if not already present
    :param conn: DB Connection object
    :param follower: follower information
    :return: True is new follower is added else False
    """

    current_follower = query_follower_by_id(conn, follower[0])

    if current_follower is not None:
        print(f"Follower with id {follower[0]} already exists")
        return False

    sql = '''INSERT INTO follower(id, name, created_at, description, 
                 followers_count, friends_count, verified)
                 VALUES(?,?,?,?,?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, follower)

    # commit change
    conn.commit()

    return True


def query_follower_by_id(conn, id):
    """
    Query follower by id
    :param conn: the Connection object
    :param id: follower id
    :return: follower details
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM follower WHERE id=?", (id,))

    row = cur.fetchone()

    return row


def insert_dm_status(conn, follower):
    """
    Add dm status into db
    :param conn: DB Connection object
    :param follower: follower information
    :return:
    """
    sql = '''INSERT INTO dm_status(id, timestamp)
                 VALUES(?,?)'''
    cur = conn.cursor()
    cur.execute(sql, follower)

    # commit change
    conn.commit()


def query_dm_status_by_id(conn, id):
    """
    Query dm status by id
    :param conn: the Connection object
    :param id: follower id
    :return: dm status information
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM dm_status WHERE id=?", (id,))

    row = cur.fetchall()

    return row


def insert_skip_user(conn, user):
    """
    Add a new follower into db if not already present
    :param conn: DB Connection object
    :param user: skip user information
    :return: True is new follower is added else False
    """

    current_follower = query_follower_by_id(conn, user[0])

    if current_follower is not None:
        print(f"Skip user with id {user[0]} already exists")
        return False

    sql = '''INSERT INTO skip_user(id, timestamp)
                 VALUES(?,?)'''
    cur = conn.cursor()
    cur.execute(sql, user)

    # commit change
    conn.commit()

    return True


def query_skip_user_by_id(conn, id):
    """
    Query skip user by id
    :param conn: the Connection object
    :param id: skip user id
    :return: follower details
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM skip_user WHERE id=?", (id,))

    row = cur.fetchone()

    return row

