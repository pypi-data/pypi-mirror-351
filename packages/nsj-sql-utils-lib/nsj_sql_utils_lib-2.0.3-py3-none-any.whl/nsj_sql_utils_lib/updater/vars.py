import os


DATABASE_PATH = os.getenv("DATABASE_PATH", "./database")


DATABASE_HOST = os.getenv("DATABASE_HOST", "")
DATABASE_NAME = os.getenv("DATABASE_NAME", "")
DATABASE_PORT = os.getenv("DATABASE_PORT", "")
DATABASE_USER = os.getenv("DATABASE_USER", "")
DATABASE_PASS = os.getenv("DATABASE_PASS", "")
VERSION = os.getenv("VERSION", "")
