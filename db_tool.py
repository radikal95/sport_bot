import  psycopg2,config
class DbQuery:
    def __init__(self):
        self.conn_string = "dbname={} user={} password={} host={}".format(config.DATABASE_URL,
                                                                          config.USERNAME,
                                                                          config.PASSWORD, config.HOST)

    def create_db_connection(self):
        return psycopg2.connect(self.conn_string)

    def close_db_connection(self, cur, conn):
        cur.close()
        conn.close()

    def execute_query(self, query, is_dml=False):
        conn = self.create_db_connection()
        cursor = None
        result = None

        try:
            cursor = conn.cursor()
            cursor.execute(query)
            if is_dml:
                conn.commit()
                result = DbQueryResponse()
            else:
                result = DbQueryResponse(value=cursor.fetchall())
        except psycopg2.Error as e:
            if cursor is not None:
                conn.rollback()
                result = DbQueryResponse(False, e.pgerror)
        except Exception as e:
            if cursor is not None:
                conn.rollback()
                result = DbQueryResponse(False, 'Error')
        finally:
            if cursor is not None:
                cursor.close()
        conn.close()
        return result

    def execute_query_wo_commit(self, cursor, query, is_dml=False):
        result = None
        try:
            cursor.execute(query)
            if is_dml:
                result = DbQueryResponse()
            else:
                result = DbQueryResponse(value=cursor.fetchall())
        except psycopg2.Error as e:
            if cursor is not None:
                result = DbQueryResponse(False, e.pgerror)
        return result


class DbQueryResponse:
    def __init__(self, is_success=True, value=None):
        self.success = is_success
        self.value = value

    def __str__(self):
        return "success : {}, value: {}".format(str(self.success), str(self.value))
