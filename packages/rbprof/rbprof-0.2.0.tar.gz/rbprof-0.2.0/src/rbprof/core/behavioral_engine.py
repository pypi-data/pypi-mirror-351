import json
import hashlib
from datetime import datetime
import os
import subprocess
import re
import socket
import psutil
import platform
from collections import defaultdict

class BehaviorEngine:
    def __init__(self):
        # Enhanced threat indicators
        self.crypto_apis = ["CryptEncrypt", "BCryptEncrypt", "CryptAcquireContext", 
                           "CryptExportKey", "CryptDestroyKey"]
        self.ransomware_ips = self._load_threat_intel("threat_intel/ips.json")
        self.ransomware_domains = self._load_threat_intel("threat_intel/domains.json")
        self.suspicious_ports = {443, 445, 3389, 8333, 8080}  # Common ransomware ports
        self.ransomware_processes = {"vssadmin", "wmic", "shadowcopy", "bitlocker", "cmd", "powershell"}
        self.suspicious_file_exts = {".encrypted", ".locked", ".crypt", ".ransom"}
        
        # Whitelists
        self.whitelisted_ips = {"8.8.8.8", "1.1.1.1", "52.114.128.0"}  # Microsoft updates
        self.whitelisted_domains = {"microsoft.com", "windowsupdate.com", "avast.com"}
        
        # Behavioral patterns
        self.file_encryption_patterns = ["encrypt", "crypt", "lock", "ransom"]
        self.persistence_mechanisms = ["CreateService", "RegSetValue", "StartupFolder"]

    def _load_threat_intel(self, filepath):
        """Load threat intelligence data from JSON files"""
        try:
            with open(filepath) as f:
                return set(json.load(f))
        except:
            return set()

    def analyze(self, filepath):
        """Enhanced ransomware analysis with comprehensive behavioral profiling"""
        try:
            if not isinstance(filepath, str):
                raise ValueError("filepath must be a string")
            if not os.path.exists(filepath):
                raise FileNotFoundError(f"File not found: {filepath}")
            
            result = {
                "filename": os.path.basename(filepath),
                "filepath": filepath,
                "status": "success",
                "timestamp": str(datetime.now()),
                "analysis": {
                    "apis": self._trace_apis(filepath),
                    "network": self._check_network(filepath),
                    "process_tree": self._get_process_tree(filepath),
                    "file_operations": self._check_file_operations(filepath),
                    "registry_operations": self._check_registry(filepath),
                    "dns_requests": self._check_dns(filepath),
                    "hashes": self._calculate_real_hashes(filepath),
                    "memory_analysis": self._check_memory(filepath)
                },
                "risk_score": 0,
                "indicators": [],
                "mitigation_suggestions": []
            }

            # Calculate comprehensive risk score
            risk_assessment = self._assess_risk(result["analysis"])
            result["risk_score"] = risk_assessment["score"]
            result["indicators"] = risk_assessment["indicators"]
            result["mitigation_suggestions"] = risk_assessment["mitigations"]
            
            return result

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "filename": os.path.basename(filepath) if isinstance(filepath, str) else "unknown",
                "timestamp": str(datetime.now())
            }

    def _trace_apis(self, filepath):
        """Trace API calls with enhanced detection"""
        try:
            # In a real implementation, this would hook API calls
            # For demo purposes, we'll simulate detection
            detected_apis = []
            
            # Simulate checking for crypto APIs
            if "malware" in filepath.lower():
                detected_apis.extend(["CryptEncrypt", "BCryptEncrypt", "DeleteShadowCopies"])
            
            # Check for persistence mechanisms
            if "persist" in filepath.lower():
                detected_apis.extend(self.persistence_mechanisms)
            
            return detected_apis
        except:
            return []

    def _check_network(self, filepath):
        """Comprehensive network analysis with threat intelligence"""
        try:
            connections = self._get_real_network_connections()
            suspicious_conns = []
            c2_patterns = []
            
            for conn in connections:
                conn["threat_indicators"] = []
                
                # IP reputation check
                if conn["remote_ip"] in self.ransomware_ips:
                    conn["threat_indicators"].append(
                        f"Connection to known ransomware IP {conn['remote_ip']}"
                    )
                
                # Suspicious port check
                if conn["remote_port"] in self.suspicious_ports:
                    conn["threat_indicators"].append(
                        f"Connection to suspicious port {conn['remote_port']}"
                    )
                
                # Process legitimacy check
                if conn.get("process"):
                    proc_name = conn["process"].get("name", "").lower()
                    if any(rp in proc_name for rp in self.ransomware_processes):
                        conn["threat_indicators"].append(
                            f"Suspicious process '{proc_name}' making network calls"
                        )
                
                if conn["threat_indicators"]:
                    suspicious_conns.append(conn)
            
            # Detect C2 patterns
            c2_patterns = self._detect_c2_communication(connections)
            
            return {
                "suspicious": len(suspicious_conns) > 0 or len(c2_patterns) > 0,
                "connections": connections,
                "suspicious_connections": suspicious_conns,
                "c2_patterns": c2_patterns,
                "timestamp": str(datetime.now())
            }
        except Exception as e:
            return {
                "suspicious": False,
                "error": f"Network analysis failed: {str(e)}",
                "timestamp": str(datetime.now())
            }

    def _get_real_network_connections(self):
        """Get actual network connections with process info"""
        connections = []
        
        try:
            net_conns = psutil.net_connections(kind='inet')
            for conn in net_conns:
                if conn.status == psutil.CONN_ESTABLISHED:
                    connection = {
                        "protocol": "TCP" if conn.type == socket.SOCK_STREAM else "UDP",
                        "local_ip": conn.laddr.ip,
                        "local_port": conn.laddr.port,
                        "remote_ip": conn.raddr.ip if conn.raddr else None,
                        "remote_port": conn.raddr.port if conn.raddr else None,
                        "state": conn.status,
                        "pid": conn.pid,
                        "process": self._get_process_info(conn.pid)
                    }
                    connections.append(connection)
        except:
            pass
            
        return connections

    def _get_process_info(self, pid):
        """Get detailed process information"""
        try:
            p = psutil.Process(pid)
            return {
                "pid": pid,
                "name": p.name(),
                "exe": p.exe(),
                "cmdline": p.cmdline(),
                "create_time": datetime.fromtimestamp(p.create_time()).isoformat(),
                "status": p.status()
            }
        except:
            return {}

    def _detect_c2_communication(self, connections):
        """Detect command and control communication patterns"""
        patterns = []
        freq = defaultdict(int)
        
        # Beaconing detection
        for conn in connections:
            if conn["remote_ip"]:
                key = f"{conn['remote_ip']}:{conn['remote_port']}"
                freq[key] += 1
        
        for endpoint, count in freq.items():
            if count > 5:  # Beaconing threshold
                patterns.append(f"Potential beaconing to {endpoint} ({count} connections)")
        
        # DNS tunneling detection
        dns_queries = [c for c in connections if c["remote_port"] == 53]
        if len(dns_queries) > 10:  # Excessive DNS queries
            patterns.append(f"Excessive DNS queries ({len(dns_queries)}), possible DNS tunneling")
        
        return patterns

    def _get_process_tree(self, filepath):
        """Get actual process tree with relationships"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'ppid', 'exe']):
                try:
                    processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "ppid": proc.info['ppid'],
                        "exe": proc.info['exe']
                    })
                except:
                    continue
            
            # Build process tree relationships
            process_tree = []
            for proc in processes:
                parent = next((p for p in processes if p['pid'] == proc['ppid']), None)
                if parent:
                    process_tree.append(f"{parent['name']} ({parent['pid']}) → {proc['name']} ({proc['pid']})")
            
            # Check for suspicious process chains
            suspicious_chains = []
            for chain in process_tree:
                if any(proc.lower() in chain.lower() for proc in self.ransomware_processes):
                    suspicious_chains.append(chain)
            
            return {
                "all_processes": process_tree,
                "suspicious_chains": suspicious_chains
            }
        except:
            return {"error": "Process tree analysis failed"}

    def _check_file_operations(self, filepath):
        """Monitor for suspicious file operations"""
        try:
            # In a real implementation, this would monitor file system activity
            # For demo, we'll simulate detection
            suspicious_ops = []
            
            if "malware" in filepath.lower():
                suspicious_ops.extend([
                    "Mass file renaming detected",
                    "Suspicious file extensions created: .encrypted, .locked"
                ])
            
            return {
                "suspicious": len(suspicious_ops) > 0,
                "operations": suspicious_ops,
                "timestamp": str(datetime.now())
            }
        except:
            return {"suspicious": False, "error": "File operation monitoring failed"}

    def _check_registry(self, filepath):
        """Check for suspicious registry modifications"""
        try:
            # Simulate registry check
            suspicious_changes = []
            
            if "malware" in filepath.lower():
                suspicious_changes.extend([
                    "Registry modification: HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                    "Registry modification: HKLM\\System\\CurrentControlSet\\Services"
                ])
            
            return {
                "suspicious": len(suspicious_changes) > 0,
                "changes": suspicious_changes,
                "timestamp": str(datetime.now())
            }
        except:
            return {"suspicious": False, "error": "Registry analysis failed"}

    def _check_dns(self, filepath):
        """Analyze DNS requests for suspicious domains"""
        try:
            # Simulate DNS check
            suspicious_queries = []
            
            if "malware" in filepath.lower():
                suspicious_queries.extend([
                    "DNS query for malicious-domain.com",
                    "DNS query for c2-server.net"
                ])
            
            return {
                "suspicious": len(suspicious_queries) > 0,
                "queries": suspicious_queries,
                "timestamp": str(datetime.now())
            }
        except:
            return {"suspicious": False, "error": "DNS analysis failed"}

    def _calculate_real_hashes(self, filepath):
        """Calculate actual file hashes"""
        try:
            with open(filepath, 'rb') as f:
                file_data = f.read()
                return {
                    "md5": hashlib.md5(file_data).hexdigest(),
                    "sha1": hashlib.sha1(file_data).hexdigest(),
                    "sha256": hashlib.sha256(file_data).hexdigest(),
                    "imphash": self._calculate_imphash(filepath),
                    "timestamp": str(datetime.now())
                }
        except Exception as e:
            return {"error": f"Hash calculation failed: {str(e)}"}

    def _calculate_imphash(self, filepath):
        """Calculate import hash (mock implementation)"""
        try:
            # In a real implementation, this would parse PE imports
            return "a1b2c3d4e5f67890"  # Mock value
        except:
            return "unknown"

    def _check_memory(self, filepath):
        """Analyze memory for suspicious patterns"""
        try:
            # Simulate memory analysis
            suspicious_patterns = []
            
            if "malware" in filepath.lower():
                suspicious_patterns.extend([
                    "Memory pattern: XOR encryption detected",
                    "Memory pattern: Process hollowing detected"
                ])
            
            return {
                "suspicious": len(suspicious_patterns) > 0,
                "patterns": suspicious_patterns,
                "timestamp": str(datetime.now())
            }
        except:
            return {"suspicious": False, "error": "Memory analysis failed"}

    def _assess_risk(self, analysis_data):
        """Comprehensive risk assessment with mitigation suggestions"""
        indicators = []
        mitigations = []
        score = 0
        
        # API call analysis (30% weight)
        suspicious_apis = [api for api in analysis_data["apis"] if api in self.crypto_apis + self.persistence_mechanisms]
        if suspicious_apis:
            score += 30
            indicators.append(f"Suspicious API calls: {', '.join(suspicious_apis)}")
            mitigations.append("Block suspicious API calls using application control")
        
        # Network analysis (25% weight)
        if analysis_data["network"].get("suspicious"):
            score += 25
            indicators.append("Suspicious network activity detected")
            mitigations.append("Isolate host from network and investigate connections")
        
        # Process tree analysis (20% weight)
        if analysis_data["process_tree"].get("suspicious_chains"):
            score += 20
            indicators.append("Suspicious process chain detected")
            mitigations.append("Terminate suspicious processes and investigate parent-child relationships")
        
        # File operations (15% weight)
        if analysis_data["file_operations"].get("suspicious"):
            score += 15
            indicators.append("Suspicious file operations detected")
            mitigations.append("Restore files from backup and monitor file system activity")
        
        # Other indicators (10% weight)
        if analysis_data["registry_operations"].get("suspicious"):
            score += 5
            indicators.append("Suspicious registry modifications detected")
            mitigations.append("Roll back registry changes and monitor registry access")
        
        if analysis_data["dns_requests"].get("suspicious"):
            score += 5
            indicators.append("Suspicious DNS queries detected")
            mitigations.append("Block malicious domains and monitor DNS traffic")
        
        return {
            "score": min(100, score),
            "indicators": indicators,
            "mitigations": mitigations
        }

# Example usage
if __name__ == "__main__":
    engine = BehaviorEngine()
    result = engine.analyze("suspicious_file.exe")
    print(json.dumps(result, indent=2))