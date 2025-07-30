from nsj_sql_utils_lib.dbadapter3 import DBAdapter3
from nsj_sql_utils_lib.dbconnection_psycopg2 import DBConnectionPsycopg2
from nsj_sql_utils_lib.updater.erp_database_updater import run_update

from nsj_sql_utils_lib.updater.vars import (
    DATABASE_HOST,
    DATABASE_NAME,
    DATABASE_PASS,
    DATABASE_PATH,
    DATABASE_PORT,
    DATABASE_USER,
    VERSION,
)
import argparse


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--dbhost", help="Database host")
    parser.add_argument("--dbname", help="Database name")
    parser.add_argument("--dbuser", help="Database user")
    parser.add_argument("--dbpass", help="Database password")
    parser.add_argument("--dbport", help="Database port")
    parser.add_argument("--dbpath", help="Database updatable files path")
    parser.add_argument("--version", help="Version of database files")

    args = vars(parser.parse_args())

    host = args["dbhost"] if args["dbhost"] is not None else DATABASE_HOST
    name = args["dbname"] if args["dbname"] is not None else DATABASE_NAME
    user = args["dbuser"] if args["dbuser"] is not None else DATABASE_USER
    _pass = args["dbpass"] if args["dbpass"] is not None else DATABASE_PASS
    port = args["dbport"] if args["dbport"] is not None else DATABASE_PORT
    path = args["dbpath"] if args["dbpath"] is not None else DATABASE_PATH
    _version = args["version"] if args["version"] is not None else VERSION

    with DBConnectionPsycopg2(
        database=name,
        host=host,
        port=port,
        user=user,
        password=_pass,
    ) as dbcon:

        adapter = DBAdapter3(dbcon.conn)
        run_update(
            adapter=adapter,
            version=_version,
            database_path=path,
        )


if __name__ == "__main__":
    main()
