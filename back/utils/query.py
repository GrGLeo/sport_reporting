from sqlalchemy import text


class Query:
    GET_TABLE_QUERY = """
        SELECT {select_statement}
        FROM {table}
        WHERE user_id = :user_id
    """

    def __init__(self, user_id, conn):
        self.user_id = user_id
        self.conn = conn

    def get_query(self, **kwargs):
        query = self.GET_TABLE_QUERY.format(table=kwargs["table"], select_statement=kwargs["select"])
        params = {'user_id': self.user_id}
        if "wkt_id" in kwargs:
            query += ' AND activity_id = :wkt_id'
            params['wkt_id'] = int(kwargs["wkt_id"])
        if "order" in kwargs:
            query += f' ORDER BY {kwargs["order"]}'
        if "limit" in kwargs:
            query += f' LIMIT {kwargs["limit"]}'
        query += ';'
        query = text(query)

        with self.conn.connect() as connection:
            result = connection.execute(query, params)
            rows = [dict(zip(result.keys(), row)) for row in result.fetchall()]
            return {"data": rows}
