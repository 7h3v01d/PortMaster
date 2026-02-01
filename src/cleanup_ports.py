import psutil
import time
import subprocess # <-- Add this import
from datetime import datetime
from core import PortManagerCore

def log(message, log_file=r"E:\S.I.M.O.N\thalamus\portmaster\cleanup_log.txt"):
    """Log message to cleanup_log.txt"""
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def cleanup_ports(ports=[8081, 8082, 8083, 49152]):
    """Clean up specified ports by terminating processes and clearing firewall rules"""
    core = PortManagerCore()
    for port in ports:
        log(f"Starting cleanup for port {port}")
        try:
            # Terminate processes using the port
            for conn in psutil.net_connections(kind='inet'):
                if conn.laddr and conn.laddr.port == port and conn.pid:
                    try:
                        process = psutil.Process(conn.pid)
                        process.terminate()
                        process.wait(timeout=5)
                        log(f"Terminated process {conn.pid} using port {port}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired) as e:
                        log(f"Failed to terminate process {conn.pid} using port {port}: {str(e)}")
            
            # Clear firewall rules
            for protocol in ['TCP', 'UDP']:
                rule_name = f"Portmaster_{protocol}_{port}"
                cmd = ['netsh', 'advfirewall', 'firewall', 'delete', 'rule', f'name={rule_name}']
                result = subprocess.run(cmd, capture_output=True, text=True) # This line needs the import
                if result.returncode == 0 and "Ok" in result.stdout:
                    log(f"Cleared firewall rule {rule_name}")
                else:
                    log(f"No firewall rule {rule_name} found or failed to clear: {result.stderr}")
            
            log(f"Cleanup completed for port {port}")
        except Exception as e:
            log(f"Cleanup failed for port {port}: {str(e)}")
    
    time.sleep(30)  # Allow TIME_WAIT to clear
    log("Cleanup completed for all ports")

if __name__ == "__main__":
    cleanup_ports()