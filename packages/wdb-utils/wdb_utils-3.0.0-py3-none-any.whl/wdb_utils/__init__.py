import pandas as pd
import yaml
import getpass
import os
from pathlib import Path
from importlib import import_module
from contextlib import contextmanager
import abc


class DatabaseConnection:

    def __init__(self, config_file=None, db_key='oracle'):
        self.db_key = db_key
        if pd.isnull(config_file):
            config = os.path.join(Path.home(), 'configs', 'config-default.yml')
        else:
            config = config_file
        if not os.path.exists(config):
            raise Exception('Config file not found {}'.format(config))
        with open(config, 'r') as ymlfile:
            self.config = yaml.load(ymlfile, yaml.FullLoader)

    @abc.abstractmethod
    def _create_connection(self):
        return

    @contextmanager
    def _connect(self):
        connection = self._create_connection()
        try:
            yield connection
        except Exception as e:
            print('Error creating database connection: {}'.format(e))

    def run_query(self, query, arraysize=120000, fetch_ct=1000000):
        results = []
        with self._connect() as connection:
            cursor = connection.cursor()
            cursor.arraysize = arraysize
            cursor.execute(query)
            while True:
                rows = cursor.fetchmany(fetch_ct)
                if not rows:
                    break
                else:
                    results = results + rows
            cols = [n[0] for n in cursor.description]

        if cols is not None:
            return pd.DataFrame(results, columns=cols)
        else:
            return

    def run_command(self, command):
        with self._connect() as connection:
            cursor = connection.cursor()
            try:
                cursor.execute(command)
            except Exception as e:
                print(e)
                raise e
            connection.commit()


class OracleConnection(DatabaseConnection):

    def __init__(self, config_file=None):
        self.oracledb = import_module('oracledb')
        self.oracledb.defaults.fetch_lobs = False
        super().__init__(config_file, 'oracle')

    def _create_connection(self):
        cfg = self.config[self.db_key]
        user = cfg['username']
        host = cfg['host']

        if 'password' in cfg:
            pwd = cfg['password']
        else:
            pwd = getpass.getpass('Database password: ')

        if 'mode' in cfg:
            mode = cfg['mode']
        else:
            mode = 'thin'

        try:
            if mode == 'thick':
                self.oracledb.init_oracle_client()

            conn = self.oracledb.connect(user=user, password=pwd, dsn=host)
            return conn
        except Exception as e:
            print('Error creating Oracle connection: {}'.format(e))
            return None

    def load_dataframe(self, data, schema, tablename):
        with self._connect() as connection:
            cursor = connection.cursor()
            inserted_data = [
                [None if pd.isnull(value) else value for value in sublist]
                for sublist in data.values.tolist()]
            sql = '''
             insert into {}.{} ({}
             ) values ({})
          '''.format(schema,
                     tablename,
                     ', '.join(["{}".format(colname) for colname in data.columns]),
                     ', '.join([":{}".format(x) for x in range(1, len(data.columns)+1)])
                     )
            try:
                cursor.executemany(sql, inserted_data)
                connection.commit()
                connection.close()

            except self.oracledb.DatabaseError as e:
                print(e)
                connection.rollback()
                connection.close()
                raise e


class SnowflakeConnection(DatabaseConnection):

    def __init__(self, config_file=None):
        super().__init__(config_file, 'snowflake')
        self.snow_connect = import_module('snowflake.connector')

    def _create_connection(self):
        self.snow_connect.paramstyle = 'numeric'

        cfg = self.config[self.db_key]
        if 'password' in cfg:
            pwd = cfg['password']
        else:
            pwd = getpass.getpass('Database password: ')

        try:
            conn = self.snow_connect.connect(
                user=cfg['username'],
                password=pwd,
                account=cfg['account'],
                database=cfg['database'],
                schema=cfg['schema']
            )
            return conn
        except Exception as e:
            print('Error creating Snowflake connection: {}'.format(e))
            return None

    def load_dataframe(self, data, schema, tablename):
        from snowflake.connector.pandas_tools import write_pandas
        data.columns = map(lambda x: str(x).upper(), data.columns)
        with self._connect() as connection:
            try:
                write_pandas(connection, data, tablename, schema=schema)
            except Exception as e:
                print(e)
                raise e


class PostgresConnection(DatabaseConnection):

    def __init__(self, config_file=None):
        self.pg_mod = import_module('psycopg2')
        self.pg_mod_sql = import_module('psycopg2.sql')
        super().__init__(config_file, db_key='postgres')

    def _create_connection(self):
        cfg = self.config[self.db_key]
        pwd = cfg.get('password') or getpass.getpass('Database password: ')
        return self.pg_mod.connect(
            user=cfg['username'],
            password=pwd,
            host=cfg['host'],
            dbname=cfg['database'],
            port=cfg['port']
        )

    def load_dataframe(self, data, schema, tablename):
        inserted_data = [
            [None if pd.isnull(value) else value for value in row]
            for row in data.values.tolist()
        ]
        columns = ', '.join([f'"{col}"' for col in data.columns])
        placeholders = ', '.join(['%s'] * len(data.columns))
        sql = '''INSERT INTO "{}"."{}" ({}) VALUES ({})'''.format(schema, tablename, columns, placeholders)

        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.executemany(sql, inserted_data)
                conn.commit()
            except self.pg_mod.DatabaseError as e:
                print(f'Error inserting into {schema}.{tablename}: {e}')
                conn.rollback()
                raise

    def replace_data(self, data: pd.DataFrame, schema: str, table: str):
        from psycopg2 import sql as pg_sql
        temp_table = f"{table}_temp"

        with self._connect() as conn:
            with conn.cursor() as cur:
                # Step 1: Create temp table with same structure
                cur.execute(
                    pg_sql.SQL("""
                        DROP TABLE IF EXISTS {temp};
                        CREATE TEMP TABLE {temp} (LIKE {schema}.{table} INCLUDING ALL);
                    """).format(
                        temp=pg_sql.Identifier(temp_table),
                        schema=pg_sql.Identifier(schema),
                        table=pg_sql.Identifier(table)
                    )
                )

                # Step 2: Insert data into temp table
                quoted_cols = [pg_sql.Identifier(col) for col in data.columns]
                placeholders = pg_sql.SQL(', ').join(pg_sql.Placeholder() * len(data.columns))
                insert_stmt = pg_sql.SQL("INSERT INTO {temp} ({columns}) VALUES ({values})").format(
                    temp=pg_sql.Identifier(temp_table),
                    columns=pg_sql.SQL(', ').join(quoted_cols),
                    values=placeholders
                )
                rows = [
                    [None if pd.isnull(x) else x for x in row]
                    for row in data.values.tolist()
                ]
                if rows:
                    cur.executemany(insert_stmt, rows)

                # Step 3: Replace original data
                cur.execute(
                    pg_sql.SQL("DELETE FROM {schema}.{table}").format(
                        schema=pg_sql.Identifier(schema),
                        table=pg_sql.Identifier(table)
                    )
                )
                cur.execute(
                    pg_sql.SQL("INSERT INTO {schema}.{table} ({columns}) SELECT {columns} FROM {temp}").format(
                        schema=pg_sql.Identifier(schema),
                        table=pg_sql.Identifier(table),
                        columns=pg_sql.SQL(', ').join(quoted_cols),
                        temp=pg_sql.Identifier(temp_table)
                    )
                )
                # Drop the temp table
                cur.execute(pg_sql.SQL("DROP TABLE IF EXISTS {temp}").format(
                    temp=pg_sql.Identifier(temp_table)
                ))

            conn.commit()


def run_query_oracle(q, config=None):
    c = OracleConnection(config)
    return c.run_query(q)


def run_command_oracle(command, config=None):
    c = OracleConnection(config)
    return c.run_command(command)


def load_data_oracle(data, schema, tablename, config=None):
    c = OracleConnection(config)
    return c.load_dataframe(data, schema, tablename)


def run_query_snowflake(q, config=None):
    c = SnowflakeConnection(config)
    return c.run_query(q)


def run_command_snowflake(command, config=None):
    c = SnowflakeConnection(config)
    return c.run_command(command)


def load_data_snowflake(data, schema, tablename, config=None):
    c = SnowflakeConnection(config)
    return c.load_dataframe(data, schema, tablename)


def run_query_postgres(q, config=None):
    c = PostgresConnection(config)
    return c.run_query(q)


def replace_data_postgres(data, schema, tablename, config=None):
    return PostgresConnection(config).replace_data(data, schema, tablename)


def run_command_postgres(command, config=None):
    c = PostgresConnection(config)
    return c.run_command(command)


def load_data_postgres(data, schema, tablename, config=None):
    c = PostgresConnection(config)
    return c.load_dataframe(data, schema, tablename)


def run_query(q, config=None):
    return run_query_oracle(q, config)


def run_command(q, config=None):
    return run_command_oracle(q, config)


def load_data(data, schema, tablename, config=None):
    return load_data_oracle(data, schema, tablename, config)
