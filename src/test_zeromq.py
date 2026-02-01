import pytest
import socket
import time
import psutil
import os
from datetime import datetime
import threading
from pathlib import Path  # Import Path
from core import find_free_port, simulate_zeromq_pub_sub

# Define the root of the test directory
TEST_ROOT = Path(__file__).resolve().parent
LOG_FILE = TEST_ROOT / "test_log_zeromq.txt"

def log(message):
    """Log message to a local test_log_zeromq.txt"""
    with open(LOG_FILE, 'a') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def is_port_bound(port, retries=10, delay=0.5):
    """
    Check if a port is bound by inspecting network connections for a LISTEN state.
    """
    log(f"Checking if port {port} is in LISTEN state...")
    for attempt in range(retries):
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'LISTEN' and conn.laddr.port == port:
                    log(f"SUCCESS: Port {port} is in LISTEN state on attempt {attempt + 1}.")
                    return True
        except psutil.AccessDenied:
            log(f"Access denied when checking connections on attempt {attempt + 1}.")
        
        time.sleep(delay)
    log(f"FAILURE: Port {port} was not found in a LISTEN state after {retries} retries.")
    return False

def cleanup(port=49152):
    log(f"Starting cleanup for port {port}")
    try:
        log(f"Active connections before cleanup: {[conn.laddr.port for conn in psutil.net_connections(kind='inet') if conn.laddr]}")
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr and conn.laddr.port == port and conn.pid:
                try:
                    process = psutil.Process(conn.pid)
                    process.terminate()
                    process.wait(timeout=5)
                    log(f"Terminated process {conn.pid} ({process.name()}) using port {port}")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired) as e:
                    log(f"Failed to terminate process {conn.pid} using port {port}: {str(e)}")
        time.sleep(1)
        log(f"Active connections after cleanup: {[conn.laddr.port for conn in psutil.net_connections(kind='inet') if conn.laddr]}")
        log(f"Cleanup completed for port {port}")
    except Exception as e:
        log(f"Cleanup failed for port {port}: {str(e)}")

@pytest.mark.parametrize("scenario", [
    "zeromq_throughput",
    "cortical_output",
    "router_simulation"
])
@pytest.mark.timeout(120)
def test_zeromq_scenarios(scenario):
    """
    Tests ZeroMQ PUB-SUB functionality for various scenarios.
    """
    cleanup()
    port, temp_socket = find_free_port()  # Get port and socket
    log(f"Testing scenario '{scenario}' on port {port}")

    result = {"success": False, "error": None}
    def run_zeromq():
        try:
            simulate_zeromq_pub_sub(port, test_mode=True, temp_socket=temp_socket)
            result["success"] = True
        except Exception as e:
            result["error"] = str(e)
            log(f"Test for '{scenario}' failed in thread: {str(e)}")

    zmq_thread = threading.Thread(target=run_zeromq)
    zmq_thread.start()

    time.sleep(2)
    port_bound = is_port_bound(port)

    zmq_thread.join(timeout=15)

    if not port_bound:
        log(f"Test for '{scenario}' failed: Port {port} not bound during test")
        pytest.fail(f"Scenario '{scenario}' failed: Port {port} not bound during test")

    if not result["success"]:
        log(f"Test for '{scenario}' failed: {result['error']}")
        pytest.fail(f"Scenario '{scenario}' failed with error: {result['error']}")

    log(f"Test for scenario '{scenario}' passed on port {port}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])