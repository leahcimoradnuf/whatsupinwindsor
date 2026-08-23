import sys
import json
import psycopg2

DATABASE_URL = sys.argv[1] # public path to db

# Alter articles table: add status column, remove UNIQUE identifier on meeting_id

# Alter assignments table: add documents_summarized and documents_available columns

