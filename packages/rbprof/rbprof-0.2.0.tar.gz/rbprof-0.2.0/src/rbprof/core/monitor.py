import json
from datetime import datetime
import numpy as np
from typing import Dict, Any


class MonitoringModule:
    @staticmethod
    def calculate_entropy(data: bytes) -> float:
        """Compute Shannon entropy (0-8 scale)"""
        if not data:
            return 0.0
        entropy = 0.0
        for x in range(256):
            p_x = data.count(x) / len(data)
            if p_x > 0:
                entropy += -p_x * np.log2(p_x)
        return entropy

    def scan(self, filepath: str) -> Dict[str, Any]:
        """Transform X → X' with initial flags"""
        try:
            with open(filepath, "rb") as f:
                data = f.read()
            
            return {
                "file": filepath,
                "entropy": float(self.calculate_entropy(data)),  
                "size_MB": float(len(data) / (1024 * 1024)),    
                "extension": str(filepath.split(".")[-1]),       
                "is_suspicious": bool(self.calculate_entropy(data) > 7.0)  
            }
        except Exception as e:
            return {
                "error": str(e),
                "file": filepath,
                "is_suspicious": False
            }

class SafeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.floating)):
            return int(obj) if isinstance(obj, np.integer) else float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

if __name__ == "__main__":
    monitor = MonitoringModule()
    
    # Test with both normal and suspicious files
    for file in ["normal.docx", "malware.exe"]:
        try:
            x_prime = monitor.scan(file)
            print(f"Scan results for {file}:")
            print(json.dumps(x_prime, indent=2, cls=SafeEncoder))
        except Exception as e:
            print(f"Error scanning {file}: {str(e)}")