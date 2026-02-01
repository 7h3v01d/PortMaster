import pytest
from unittest.mock import MagicMock, mock_open
from core import PortManagerCore

@pytest.fixture
def mock_core(mocker):
    """Fixture to create a mocked instance of PortManagerCore."""
    # Mock dependencies that interact with the system
    mocker.patch('psutil.net_connections', return_value=[])
    mocker.patch('psutil.Process', return_value=MagicMock())
    mocker.patch('psutil.pid_exists', return_value=True)
    mocker.patch('subprocess.run', return_value=MagicMock(returncode=0, stdout="Ok.", stderr=""))
    mocker.patch('socket.socket', new_callable=MagicMock)
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('builtins.open', mock_open(read_data='{}'))
    mocker.patch('json.load', return_value={})
    mocker.patch('json.dump')

    core = PortManagerCore()
    # Mock the internal logger to prevent file I/O
    mocker.patch.object(core, 'log')
    return core