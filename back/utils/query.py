from sqlalchemy import text


class Query:
    GET_TABLE_QUERY = """
        SELECT {select_statement}
        FROM {table}
        WHERE user_id = :user_id
    """

    def __init__(self, table, select, user_id, conn):
        self.user_id = user_id
        self.conn = conn
        self.table = table
        self.select = select

    def get_query(self, **kwargs):
        query = self.GET_TABLE_QUERY.format(table=self.table, select_statement=self.select)
        params = {'user_id': self.user_id}

        if "wkt_id" in kwargs:
            query += ' AND activity_id = :wkt_id'
            params['wkt_id'] = int(kwargs["wkt_id"])
        if "order_by" in kwargs:
            query += f' ORDER BY {kwargs["rder_by"]}'
        if "limit" in kwargs:
            query += f' LIMIT {kwargs["imit"]}'

        query += ';'
        query = text(query)
        with self.conn.connect() as connection:
            result = connection.execute(query, params)
            print(query)
            print(result.fetchall())
            return
            rows = [dict(row) for row in result]
            return {"data": rows}
