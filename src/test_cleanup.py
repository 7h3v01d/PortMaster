import pytest
from unittest.mock import MagicMock, call
import psutil

from cleanup_ports import cleanup_ports, log

@pytest.fixture
def mock_cleanup_deps(mocker):
    """Mock dependencies for the cleanup script."""
    mocker.patch('cleanup_ports.log')
    mocker.patch('time.sleep')

    # FIX: Create a mock address object with a .port attribute.
    laddr_mock = MagicMock()
    laddr_mock.port = 8081

    mock_conn = MagicMock()
    mock_conn.laddr = laddr_mock # Use the new address mock
    mock_conn.pid = 5678
    mocker.patch('psutil.net_connections', return_value=[mock_conn])
    
    mock_process = MagicMock()
    mocker.patch('psutil.Process', return_value=mock_process)

    mock_run = mocker.patch('subprocess.run', return_value=MagicMock(returncode=0, stdout="Ok."))
    
    return mock_process, mock_run

def test_cleanup_ports(mock_cleanup_deps):
    """Test the main cleanup function."""
    mock_process, mock_run = mock_cleanup_deps
    
    ports_to_clean = [8081, 9999]
    cleanup_ports(ports=ports_to_clean)
    
    psutil.Process.assert_called_once_with(5678)
    mock_process.terminate.assert_called_once()
    
    assert mock_run.call_count == 4
    
    # FINAL FIX: Add the missing keyword arguments to match the actual call in cleanup_ports.py
    expected_calls = [
        call(['netsh', 'advfirewall', 'firewall', 'delete', 'rule', 'name=Portmaster_TCP_8081'], capture_output=True, text=True),
        call(['netsh', 'advfirewall', 'firewall', 'delete', 'rule', 'name=Portmaster_UDP_8081'], capture_output=True, text=True),
        call(['netsh', 'advfirewall', 'firewall', 'delete', 'rule', 'name=Portmaster_TCP_9999'], capture_output=True, text=True),
        call(['netsh', 'advfirewall', 'firewall', 'delete', 'rule', 'name=Portmaster_UDP_9999'], capture_output=True, text=True)
    ]
    mock_run.assert_has_calls(expected_calls, any_order=True)