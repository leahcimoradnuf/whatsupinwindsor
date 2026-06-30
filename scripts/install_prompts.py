import os
import sys
import json
import psycopg2

DATABASE_URL = sys.argv[1] # public path to db
PROMPTS = sys.argv[2] # private path to prompts.json

def load_prompts(file):
    with open(file, 'r') as f:
        prompts = json.loads(f.read())
    return prompts

def main():
    """Read prompts data and install it to prod db
    """
    # Load the prompt messages
    prompt_data = load_prompts(PROMPTS)

    conn = None
    cur = None

    # Connect to db
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("connected")  
        # Write to db
        cur = conn.cursor()

        # Create tables
        cur.execute(
            """CREATE TABLE IF NOT EXISTS system_prompts (
            id SERIAL PRIMARY KEY,
            doc_type TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL
            );"""
            )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS few_shot_examples (
            id SERIAL PRIMARY KEY,
            meeting_id TEXT NOT NULL,
            doc_type TEXT NOT NULL,
            document_text TEXT NOT NULL,
            meeting_date DATE,
            expected_output JSONB NOT NULL,
            UNIQUE (meeting_id, doc_type));"""
            )
        
        # System prompt for minutes
        # TODO build out for other doc types when necessary
        cur.execute(
            """INSERT INTO system_prompts (doc_type, content)
            VALUES (%s, %s)
            ON CONFLICT (doc_type) DO UPDATE SET
                content = EXCLUDED.content
            """,
            ("minutes", prompt_data["minutes"]["system"])
        )
    
        for few_shot in prompt_data["minutes"]["examples"]:
            doc_type = "minutes"
            expected_output = {
                "meeting_date": few_shot["meeting_date"],
                "meeting_id": few_shot["meeting_id"],
                "headline": few_shot["headline"],
                "bullets": few_shot["bullets"],
                "blurb": few_shot["blurb"]
            }
            cur.execute(
                """INSERT INTO few_shot_examples (meeting_id, doc_type, document_text, meeting_date, expected_output)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (meeting_id, doc_type) DO UPDATE SET
                    document_text = EXCLUDED.document_text,
                    expected_output = EXCLUDED.expected_output
                """,
                (few_shot["meeting_id"], doc_type, few_shot["minutes_text"], few_shot["meeting_date"], json.dumps(expected_output))
            )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        if cur: cur.close()
        if conn: conn.close()

if __name__ == "__main__":
    main()