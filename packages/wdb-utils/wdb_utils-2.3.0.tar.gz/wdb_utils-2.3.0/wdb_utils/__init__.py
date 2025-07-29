import pandas as pd
import yaml
import getpass
import os
from pathlib import Path
from importlib import import_module
from contextlib import contextmanager


class RelationalConnection:

    def __init__(self, config_file=None, db_key=None):
        self.db_key = db_key
        self.config = self._load_config(config_file)

    def _load_config(self, config_file):
        config_path = config_file or os.path.join(Path.home(), 'configs', 'config-default.yml')
        if not os.path.exists(config_path):
            raise FileNotFoundError(f'Config file not found: {config_path}')
        with open(config_path, 'r') as f:
            return yaml.load(f, yaml.FullLoader)

    @contextmanager
    def _connect(self):
        connection = self._create_connection()
        try:
            yield connection
        finally:
            if connection:
                connection.close()

    def run_query(self, query, arraysize=120000, fetch_ct=1000000):
        results, cols = [], None
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.arraysize = arraysize
            cursor.execute(query)
            while True:
                rows = cursor.fetchmany(fetch_ct)
                if not rows:
                    break
                results.extend(rows)
            cols = [desc[0] for desc in cursor.description]
        return pd.DataFrame(results, columns=cols) if cols else None

    def run_command(self, command):
        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(command)
                conn.commit()
            except Exception as e:
                print(f'Error running command: {e}')
                conn.rollback()
                raise

    def load_dataframe(self, data, schema, tablename):
        raise NotImplementedError("This method should be implemented in subclasses")


class PostgresConnection(RelationalConnection):

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


class OracleConnection(RelationalConnection):

    def __init__(self, config_file=None):
        self.oracledb = import_module('oracledb')
        self.oracledb.defaults.fetch_lobs = False
        super().__init__(config_file, db_key='oracle')

    def _create_connection(self):
        cfg = self.config[self.db_key]
        pwd = cfg.get('password') or getpass.getpass('Database password: ')
        if cfg.get('mode', 'thin') == 'thick':
            self.oracledb.init_oracle_client()
        return self.oracledb.connect(user=cfg['username'], password=pwd, dsn=cfg['host'])

    def load_dataframe(self, data, schema, tablename):
        data = self.coerce_boolean_columns(data)
        inserted_data = [
            [None if pd.isnull(value) else value for value in row]
            for row in data.values.tolist()
        ]
        colnames = ', '.join(data.columns)
        bindvars = ', '.join([f":{i+1}" for i in range(len(data.columns))])
        sql = f'INSERT INTO {schema}.{tablename} ({colnames}) VALUES ({bindvars})'
        with self._connect() as conn:
            cursor = conn.cursor()
            try:
                cursor.executemany(sql, inserted_data)
                conn.commit()
            except self.oracledb.DatabaseError as e:
                print(f'Oracle error: {e}')
                conn.rollback()
                raise


class SnowflakeConnection(RelationalConnection):

    def __init__(self, config_file=None):
        self.sf = import_module('snowflake.connector')
        super().__init__(config_file, db_key='snowflake')

    def _create_connection(self):
        cfg = self.config[self.db_key]
        pwd = cfg.get('password') or getpass.getpass('Database password: ')
        return self.sf.connect(
            user=cfg['username'],
            password=pwd,
            account=cfg['account'],
            database=cfg['database'],
            schema=cfg['schema']
        )

    def load_dataframe(self, data, schema, tablename):
        from snowflake.connector.pandas_tools import write_pandas
        data.columns = map(lambda x: str(x).upper(), data.columns)
        with self._connect() as conn:
            try:
                write_pandas(conn, data, tablename, schema=schema)
            except Exception as e:
                print(f'Snowflake error: {e}')
                raise


def load_csv_to_db(csv_path, schema, tablename, conn_cls, config=None):
    df = pd.read_csv(csv_path)
    conn = conn_cls(config)
    conn.load_dataframe(df, schema, tablename)


def run_query_postgres(q, config=None):
    return PostgresConnection(config).run_query(q)


def run_command_postgres(command, config=None):
    return PostgresConnection(config).run_command(command)


def load_data_postgres(data, schema, tablename, config=None):
    return PostgresConnection(config).load_dataframe(data, schema, tablename)


def replace_data(data, schema, tablename, config=None):
    return PostgresConnection(config).replace_data(data, schema, tablename)


def run_query_oracle(q, config=None):
    return OracleConnection(config).run_query(q)


def run_command_oracle(command, config=None):
    return OracleConnection(config).run_command(command)


def load_data_oracle(data, schema, tablename, config=None):
    return OracleConnection(config).load_dataframe(data, schema, tablename)


def run_query_snowflake(q, config=None):
    return SnowflakeConnection(config).run_query(q)


def run_command_snowflake(command, config=None):
    return SnowflakeConnection(config).run_command(command)


def load_data_snowflake(data, schema, tablename, config=None):
    return SnowflakeConnection(config).load_dataframe(data, schema, tablename)


def run_query(q, config=None):
    return run_query_oracle(q, config)


def run_command(q, config=None):
    return run_command_oracle(q, config)


def load_data(data, schema, tablename, config=None):
    return load_data_oracle(data, schema, tablename, config)
