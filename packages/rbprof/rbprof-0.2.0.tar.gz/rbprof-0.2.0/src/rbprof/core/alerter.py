import json
import hashlib
from datetime import datetime
import numpy as np

class AlertingModule:
    @staticmethod
    def decide(x_scored):
        """Final ransomware verdict"""
        return {
            **x_scored,
            "verdict": "RANSOMWARE" if x_scored["scores"]["threat"] >= 70 else "SAFE",
            "response": "ISOLATE_AND_ROLLBACK" if x_scored["scores"]["threat"] >= 70 else "MONITOR"
        }
