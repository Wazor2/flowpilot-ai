import json
import datetime
import os

class AuditLogger:
    def __init__(self, log_file="audit_log.json"):
        self.log_file = log_file
        # Initialize the file with an empty list if it doesn't exist
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)

    def log_event(self, agent_name, action, details):
        """
        Record a timestamped JSON structured log.
        """
        event = {
            "timestamp": datetime.datetime.now().isoformat(),
            "agent": agent_name,
            "action": action,
            "details": details
        }
        
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []
            
        logs.append(event)
        
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=4)
            
        return True

    def get_logs(self):
        try:
            with open(self.log_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
