import pytest
import subprocess
from unittest.mock import MagicMock, call, mock_open
import psutil
import socket
import json

# FIX: Create a mock address object that has .ip and .port attributes, just like the real psutil object.
laddr_mock = MagicMock()
laddr_mock.ip = '127.0.0.1'
laddr_mock.port = 8080

raddr_mock = MagicMock()
raddr_mock.ip = '127.0.0.1'
raddr_mock.port = 12345

# FIX: Update MOCK_CONN to use the new address mock.
MOCK_CONN = MagicMock()
MOCK_CONN.laddr = laddr_mock
MOCK_CONN.raddr = raddr_mock
MOCK_CONN.type = socket.SOCK_STREAM
MOCK_CONN.status = 'ESTABLISHED'
MOCK_CONN.pid = 1234

MOCK_PROCESS = MagicMock()
MOCK_PROCESS.name.return_value = 'python.exe'

def test_list_connections(mock_core, mocker):
    """Test listing of active connections."""
    mocker.patch('psutil.net_connections', return_value=[MOCK_CONN])
    mocker.patch('psutil.Process', return_value=MOCK_PROCESS)

    connections = mock_core.list_connections()
    assert len(connections) == 1
    conn = connections[0]
    assert conn['Protocol'] == 'TCP'
    assert conn['Local Address'] == '127.0.0.1:8080'
    assert conn['PID'] == 1234
    assert conn['Process Name'] == 'python.exe'
    mock_core.log.assert_called_with("Listed 1 connections")

@pytest.mark.parametrize("port, in_use, expected_msg", [
    ("8080", True, "Port 8080 is in use by PID 1234 (python.exe)"),
    ("9090", False, "Port 9090 is not in use")
])
def test_check_port(mock_core, mocker, port, in_use, expected_msg):
    """Test port checking logic."""
    if in_use:
        mocker.patch('psutil.net_connections', return_value=[MOCK_CONN])
        mocker.patch('psutil.Process', return_value=MOCK_PROCESS)
    else:
        mocker.patch('psutil.net_connections', return_value=[])

    output, rc = mock_core.check_port(port)
    assert output == expected_msg
    assert rc == 0

@pytest.mark.parametrize("port, expected_rc", [("abc", 1), ("99999", 1)])
def test_check_port_invalid(mock_core, port, expected_rc):
    """Test check_port with invalid input."""
    output, rc = mock_core.check_port(port)
    assert "Error" in output
    assert rc == expected_rc

def test_kill_process(mock_core, mocker):
    """Test killing a process with confirmation."""
    mock_process_instance = MagicMock()
    mocker.patch('psutil.Process', return_value=mock_process_instance)
    
    output, rc = mock_core.kill_process("1234", confirm=True)
    
    assert output == "Terminated process 1234"
    assert rc == 0
    mock_process_instance.terminate.assert_called_once()

def test_kill_process_no_confirm(mock_core):
    """Test kill_process without confirmation."""
    output, rc = mock_core.kill_process("1234", confirm=False)
    assert "Confirmation required" in output
    assert rc == 2

def test_kill_process_not_exist(mock_core, mocker):
    """Test killing a non-existent process."""
    mocker.patch('psutil.pid_exists', return_value=False)
    output, rc = mock_core.kill_process("9999", confirm=True)
    assert "does not exist" in output
    assert rc == 1

@pytest.mark.parametrize("protocol", ["TCP", "UDP"])
def test_block_port(mock_core, mocker, protocol):
    """Test blocking a port."""
    # FIX: Ensure the mock returns a success code (0), otherwise the error branch is taken.
    mock_run = mocker.patch('subprocess.run', return_value=MagicMock(returncode=0))
    port = "8080"
    
    output, rc = mock_core.block_port(port, protocol, confirm=True)
    
    assert f"Blocked {protocol} port {port}" in output
    assert rc == 0
    expected_cmd = [
        'netsh', 'advfirewall', 'firewall', 'add', 'rule', f'name=Portmaster_{protocol}_{port}',
        'dir=in', 'action=block', f'protocol={protocol}', f'localport={port}'
    ]
    mock_run.assert_called_once_with(expected_cmd, capture_output=True, text=True)

@pytest.mark.parametrize("protocol", ["TCP", "UDP"])
def test_unblock_port(mock_core, mocker, protocol):
    """Test unblocking a port."""
    mock_run = mocker.patch('subprocess.run', return_value=MagicMock(returncode=0, stdout="Ok."))
    port = "8080"
    
    output, rc = mock_core.unblock_port(port, protocol, confirm=True)
    
    assert f"Unblocked {protocol} port {port}" in output
    assert rc == 0
    expected_cmd = [
        'netsh', 'advfirewall', 'firewall', 'delete', 'rule', f'name=Portmaster_{protocol}_{port}'
    ]
    mock_run.assert_called_once_with(expected_cmd, capture_output=True, text=True)
    
def test_reserve_port(mock_core, mocker):
    """Test port reservation logic."""
    # FIX: Ensure the mock returns a success code (0).
    mock_run = mocker.patch('subprocess.run', return_value=MagicMock(returncode=0))
    mock_json_dump = mocker.patch('json.dump')
    exe_path = r"C:\Windows\System32\notepad.exe"
    port = "8888"
    protocol = "TCP"

    m = mock_open(read_data='{}')
    mocker.patch('builtins.open', m)

    output, rc = mock_core.reserve_port(port, protocol, exe_path, confirm=True)
    
    assert f"Reserved {protocol} port {port}" in output
    assert rc == 0
    
    expected_cmd = [
        'netsh', 'advfirewall', 'firewall', 'add', 'rule', f'name=Portmaster_{protocol}_{port}',
        'dir=in', 'action=allow', f'protocol={protocol}', f'localport={port}', f'program={exe_path}'
    ]
    mock_run.assert_called_once_with(expected_cmd, capture_output=True, text=True)
    
    m.assert_called_with(mock_core.config_file, 'w')
    mock_json_dump.assert_called_once_with(
        {port: {'protocol': protocol, 'exe_path': exe_path}},
        m()
    )

def test_release_port(mock_core, mocker):
    """Test releasing a reserved port."""
    port = "8888"
    protocol = "TCP"
    mock_config = {port: {'protocol': protocol, 'exe_path': 'C:\\path.exe'}}
    mocker.patch('json.load', return_value=mock_config)
    
    mocker.patch('subprocess.run', return_value=MagicMock(returncode=0, stdout="Ok."))
    # FIX: Assign the mock_open instance to a variable to reference it later.
    m = mock_open()
    mocker.patch('builtins.open', m)
    mock_json_dump = mocker.patch('json.dump')

    output, rc = mock_core.release_port(port, confirm=True)
    
    assert f"Released {protocol} port {port}" in output
    assert rc == 0
    
    # FIX: Assert against the mock instance's file handle `m()`.
    mock_json_dump.assert_called_once_with({}, m())

def test_save_connections(mock_core, mocker):
    """Test saving connections to a file."""
    mocker.patch.object(mock_core, 'list_connections', return_value=[
        {"Protocol": "TCP", "Local Address": "a", "Remote Address": "b", "Status": "c", "PID": 1, "Process Name": "d"}
    ])
    
    m = mock_open()
    mocker.patch('builtins.open', m)
    
    filename = "output.txt"
    output, rc = mock_core.save_connections(filename)
    
    assert f"Saved 1 connections to {filename}" in output
    assert rc == 0
    m.assert_called_once_with(filename, 'w')
    handle = m()
    assert handle.write.call_count > 3