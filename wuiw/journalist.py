import os
import logging
import json
from openai import OpenAI
from wuiw.config_prompts import EXAMPLE_MINUTES, EXAMPLE_HEADLINE, EXAMPLE_BULLETS, EXAMPLE_BLURB, EXAMPLE_MEETING_DATE


logger = logging.getLogger(__name__)

[REDACTED]

class OpenAIProvider:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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
        response = self.client.chat.completions.create(
            model=self.model,
            response_format={"type": "json_object"},
            messages=prompt
        )
        response_data = json.loads(response.choices[0].message.content)

        return response_data