import os

from haf_plug_play.server.system_status import SystemStatus

WDIR_FOLLOW = os.path.dirname(__file__)

class SearchQuery:

    @classmethod
    def follow(cls, follower_account=None, followed_account=None, block_range=None):
        if block_range is None:
            latest = SystemStatus.get_latest_block()
            if not latest: return None # TODO: notify??
            block_range = [latest - 28800, latest]
        query = f"""
                    SELECT transaction_id, req_posting_auths, account, following, what
                    FROM hpp_follow
                    WHERE block_num BETWEEN {block_range[0]} AND {block_range[1]}
        """
        if follower_account:
            query += f"AND account = '{follower_account}'"
        if followed_account:
            query += f"AND following = '{followed_account}';"

        return query


class StateQuery:

    @classmethod
    def get_account_followers(cls, account):
        query = f"""
            SELECT account, what
                FROM hpp_follow_state
                WHERE following = '{account}'
                AND what != '{{}}';
        """
        return query
