import sys
import json
import psycopg2

DATABASE_URL = sys.argv[1] # public path to db

# Alter articles table: add status and doc_url columns, remove UNIQUE identifier on meeting_id


