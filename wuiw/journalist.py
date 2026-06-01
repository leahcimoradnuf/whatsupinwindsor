import os
import logging
import json
import psycopg2
import psycopg2.extras
from openai import OpenAI
from anthropic import Anthropic
from wuiw.config import get_db_connection
from wuiw.config_prompts import EXAMPLE_MINUTES, EXAMPLE_HEADLINE, EXAMPLE_BULLETS, EXAMPLE_BLURB, EXAMPLE_MEETING_DATE


logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

def _build_prompts(doc_type, body=None):
    # Query system prompts and few shots
    # TODO handle case where doc_type is not in db
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """SELECT content FROM system_prompts
        WHERE doc_type = %s""",
        (doc_type,)
        )
    _system_prompts = cur.fetchall()
    cur.execute(
        """SELECT document_text, meeting_date, expected_output FROM few_shot_examples
        WHERE doc_type = %s""",
        (doc_type,)
    )
    _example_prompts = cur.fetchall()
    cur.close()
    conn.close()

    return _system_prompts, _example_prompts

class OpenAIProvider:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = "gpt-4o-mini"
        self.prompts = {
            "minutes": MINUTES_FEW_SHOTS,
            "agenda": AGENDA_FEW_SHOTS,
            "votes": VOTES_FEW_SHOTS
        }
    
    def summarize(self, text, doc_type):
        # provider-specific API call here
        if doc_type not in self.prompts:
            raise ValueError(f"Unknown doc_type: {doc_type}") # handle with logger.warning in writer.py
        
        task = {
            "role": "user",
            "content": text
        }

        prompt = self.prompts[doc_type] + [task]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=prompt
            )
            response_data = json.loads(response.choices[0].message.content)
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens

            return (response_data, "OK", input_tokens, output_tokens)
        except Exception as e:
            logger.warning(f"AI client failed: {e}")
            return (None, "FAIL", None, None)
    
class AnthropicProvider:
    """Class to instantiate Anthropic API client
    """
    def __init__(self):
        self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        self.model = "claude-sonnet-4-6"

    def summarize(self, text, doc_type):
        """Constructs a prompt and summarizes assigned text.

        Args:
            text (str): body of text downloaded from government document
            doc_type (str): document type identifier (minutes, agenda, etc..). For constructing prompt.

        Raises:
            ValueError: When an invalid doc_type is passed

        Returns:
            response (tup): (response_data, API Status, N_input_tokens, N_output_tokens)
        """
        system_prompt, example_prompts = _build_prompts(doc_type)

        # if doc_type not in system_prompt:
        #     raise ValueError(f"Unknown doc_type: {doc_type}")
        
        few_shots = []
        for example in example_prompts:
            few_shot = [{
                "role": "user",
                "content": example["document_text"]
            },{
                "role": "assistant",
                "content": json.dumps(example["expected_output"])
            }]
            few_shots += few_shot

        task = {
            "role": "user",
            "content": text
            }
        
        prompt = few_shots + [task]

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt[0]["content"],
                messages=prompt
                )
    
            response_data =  json.loads(response.content[0].text)
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            return (response_data, "OK", input_tokens, output_tokens)
        except Exception as e:
            logger.warning(f"AI client failed: {e}")
            return (None, "FAIL", None, None)
    

# Providers Registry
providers = {
    "OpenAI": OpenAIProvider,
    "Anthropic": AnthropicProvider
}