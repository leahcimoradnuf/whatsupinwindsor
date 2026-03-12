import os
import logging
import json
from openai import OpenAI
from wuiw.config_prompts import EXAMPLE_MINUTES, EXAMPLE_HEADLINE, EXAMPLE_BULLETS, EXAMPLE_BLURB, EXAMPLE_MEETING_DATE


logger = logging.getLogger(__name__)

MINUTES_FEW_SHOTS = [
    {
        "role": "system",
        "content": """
        You are a neutral, factual reporter who writes concise summaries of official government meeting minutes.
        Your summaries include an impactful headline, a bulleted list of important decisions or discussion points, and a short blurb
        (3-7 sentances) summarizing the key takeaways. Writing style should be factual and almost boring. Target audience is civic-minded 
        and already engaged, they just want to know what happened in 2 minutes or less.
        
        Always respond in valid JSON with this exact structure:
        {
            "meeting_date": "string; in ISO 8601 format (YYYY-MM-DD)",
            "headline": "string",
            "bullets": ["string"],
            "blurb": "string"
        }
        Do not include any text outside the JSON.
        """
    },{
        "role": "user",
        "content": EXAMPLE_MINUTES[0]
    },{
        "role": "assistant",
        "content": json.dumps({"meeting_date": EXAMPLE_MEETING_DATE[0], "headline": EXAMPLE_HEADLINE[0], "bullets": EXAMPLE_BULLETS[0],"blurb": EXAMPLE_BLURB[0]})
    },{
        "role": "user",
        "content": EXAMPLE_MINUTES[1]
    },{
        "role": "assistant",
        "content": json.dumps({"meeting_date": EXAMPLE_MEETING_DATE[1], "headline": EXAMPLE_HEADLINE[1], "bullets": EXAMPLE_BULLETS[1],"blurb": EXAMPLE_BLURB[1]})
    }
]
AGENDA_FEW_SHOTS = ""
VOTES_FEW_SHOTS = ""

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