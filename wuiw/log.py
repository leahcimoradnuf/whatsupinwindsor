class CivicRequestLog:
    def __init__(self):
        self.run_id = None
        self.info = []

    def set_run_id(self, run_id):
        self.run_id = run_id

    def record(self, timestamp, url, status):
        self.info.append((self.run_id, timestamp, url, status))

    def reset(self):
        self.run_id = None
        self.info.clear()

class AIRequestLog:
    def __init__(self):
        self.run_id = None
        self.info = []
    
    def set_run_id(self, run_id):
        self.run_id = run_id

    def record(self, timestamp, provider, status, input_tokens, output_tokens):
        self.info.append((self.run_id, timestamp, provider, status, input_tokens, output_tokens))

    def reset(self):
        self.run_id = None
        self.info.clear()

civic_log = CivicRequestLog()
ai_log = AIRequestLog()