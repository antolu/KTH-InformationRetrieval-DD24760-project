import logging
import time
import sqlite3

# FOR DEBUG USE
# logging.basicConfig(
#         filename='/var/log/usr_prof.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s',
#         level=logging.DEBUG)

logger = logging.getLogger('UserProfileLogger')
class UserProfileLogger:

    USER_PROFILE_DB = "usr_profile_db/user_profile.db"

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        logger.debug("Closing the database connection")
        self.conn.close()

    def __init__(self, user_email):
        self.conn = sqlite3.connect(self.USER_PROFILE_DB)
        logger.debug("Using the profile database: %s", self.USER_PROFILE_DB)

        self.user_id = self._get_user_id(user_email)
        logger.debug("Initialized UserProfileLogger: user_id = %s", self.user_id)

    def _get_user_id(self, user_email):
        sql = "SELECT id FROM users WHERE email='{}';".format(user_email)
        cur = self.conn.cursor()
        cur.execute(sql)
        row = cur.fetchone()

        if row is None:
            logger.debug(
                "User email %s not found in the database. No profiling for the user", user_email)
            ret = None
        else:
            # parse user id
            ret = row[0]
        return ret

    @staticmethod
    def _insert_col_val_to_db_table(db_conn, table_name, col_val):

        # create a sql with placeholder
        col = ','.join(col_val.keys())
        placeholders = ':'+', :'.join(col_val.keys())
        sql = "INSERT INTO {} ({}) VALUES({});".format(table_name, col, placeholders)

        # execute the command
        cur = db_conn.cursor()
        cur.execute(sql, col_val)
        db_conn.commit()

    def log_search(self, query, query_type, ranking_type=None):
        if self.user_id is None:
            return

        # build col_val dict
        col_val = {
            'userid': str(self.user_id),
            'posix_time': str(int(time.time())),
            'query': query,
            'query_type': query_type,
            'ranking_type': ranking_type
        }
        # log the dictionary for debugging
        logger.debug('[user_search_log] profile: %s', col_val)
        self._insert_col_val_to_db_table(self.conn, "user_search_log", col_val)

    def log_retrieved(self, selected_doc):
        if self.user_id is None:
            return
        col_val = {
            'userid': str(self.user_id),
            'posix_time': str(int(time.time())),
            'selected_doc': selected_doc
        }
        logger.debug('[user_retrieved_log] profile: %s', col_val)
        self._insert_col_val_to_db_table(self.conn, "user_retrieved_log", col_val)

if __name__ == "__main__":
    import sqlite3
    logging.basicConfig(level=logging.DEBUG)
    usr_email = "chlin3@kth.se"
    # Developers can alway change the profile db like this
    # UserProfileLogger.USER_PROFILE_DB = "myfoler/userprofile.db"
    # ========================================================================
    with UserProfileLogger(usr_email) as profile_logger:
        # log search
        profile_logger.log_search(
            query="zombie", query_type="intersection", ranking_type=None)
        profile_logger.log_search(
            query="zombie attack", query_type="phase", ranking_type=None)
        profile_logger.log_search(
            query="zombie attack", query_type="ranking", ranking_type="tf-idf")

        # log retrieved
        profile_logger.log_retrieved(selected_doc="Zombie_Walk.f")