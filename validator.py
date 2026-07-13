import json
import hashlib

class AAAPValidator:
    def __init__(self, log_file):
        with open(log_file, 'r') as f:
            self.log_data = json.load(f)

    def validate_all(self):
        # 1. Schema Validation (AAAP-003)
        if not self._check_schema():
            return "AAAP-003: Schema Validation Failed"
        
        # 2. Hash Chain & Timestamp Validation (AAAP-001, AAAP-002)
        prev_hash = "0" * 64
        prev_time = "1970-01-01T00:00:00Z"
        
        for entry in self.log_data:
            # Check Chronology (AAAP-002)
            if entry['timestamp'] <= prev_time:
                return "AAAP-002: Timestamp Chronology Error"
            
            # Check Integrity (AAAP-001)
            if entry['previous_hash'] != prev_hash:
                return "AAAP-001: Invalid Hash Chain"
            
            # Update State
            raw_data = json.dumps(entry['data'], sort_keys=True)
            prev_hash = hashlib.sha256(raw_data.encode()).hexdigest()
            prev_time = entry['timestamp']
            
        return "PASS: Chain Integrity Verified"

    def _check_schema(self):
        required = {'timestamp', 'event_id', 'trigger_type', 'previous_hash', 'data'}
        return all(required.issubset(e.keys()) for e in self.log_data)
