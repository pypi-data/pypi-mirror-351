import json
import hashlib
from datetime import datetime
import numpy as np  

class DetectionModule:
    def __init__(self):
        self.encryption_threshold = 50  
    
    def evaluate(self, x_double_prime):
        """Compute detection scores and flags"""
        
        encryption_score = min(100, x_double_prime.get("encrypted_files", 0) * 2)
        
        
        flags = {
            "crypto_api_used": any(api in x_double_prime["apis"] 
                               for api in ["CryptEncrypt", "BCryptEncrypt"]),
            "c2_detected": len(x_double_prime["network"]["connections"]) > 0,
            "vss_deleted": "DeleteShadowCopies" in x_double_prime["apis"]
        }
        
        
        threat_score = (
            0.4 * encryption_score +
            0.3 * (100 if flags["c2_detected"] else 0) +
            0.3 * (100 if flags["vss_deleted"] else 0)
        )
        
        return {
            **x_double_prime,
            "scores": {
                "encryption": encryption_score,
                "threat": threat_score
            },
            "flags": flags
        }