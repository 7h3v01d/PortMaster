import pytest
from PyQt6.QtWidgets import QApplication, QMessageBox, QPushButton
from PyQt6.QtCore import Qt
from gui import PortManagerGUI

def find_button_by_text(widget, text):
    """Helper to find a button in a widget's children by its text."""
    buttons = widget.findChildren(QPushButton)
    for button in buttons:
        if button.text() == text:
            return button
    return None

@pytest.fixture
def app(qtbot, mocker):
    """Fixture to create and setup the GUI application."""
    mock_core_instance = mocker.MagicMock()
    mocker.patch('gui.PortManagerCore', return_value=mock_core_instance)
    
    mocker.patch.object(QMessageBox, 'question', return_value=QMessageBox.StandardButton.Yes)
    
    test_app = PortManagerGUI()
    qtbot.addWidget(test_app)
    return test_app, mock_core_instance

def test_gui_list_connections(app, qtbot):
    """Test the 'List Connections' button."""
    gui, core = app
    
    mock_data = [
        {"Protocol": "TCP", "Local Address": "a", "Remote Address": "b", "Status": "c", "PID": 1, "Process Name": "d"}
    ]
    core.list_connections.return_value = mock_data
    
    # FIX: Find the button by its text using a helper function.
    list_button = find_button_by_text(gui, "List Connections")
    assert list_button is not None
    # FIX: Use the correct constant for the mouse click.
    qtbot.mouseClick(list_button, Qt.MouseButton.LeftButton)
    
    assert gui.connections_table.rowCount() == 1
    assert gui.connections_table.item(0, 0).text() == "TCP"
    assert gui.connections_table.item(0, 5).text() == "d"
    core.list_connections.assert_called_once()

def test_gui_check_port(app, qtbot):
    """Test the 'Check Port' functionality."""
    gui, core = app
    
    gui.notebook.setCurrentIndex(1)
    
    core.check_port.return_value = ("Port 8080 is in use", 0)
    
    gui.port_entry.setText("8080")
    # FIX: Correctly find the button and click.
    check_button = find_button_by_text(gui.notebook.currentWidget(), "Check")
    assert check_button is not None
    qtbot.mouseClick(check_button, Qt.MouseButton.LeftButton)
    
    assert gui.pm_output_text.toPlainText() == "Port 8080 is in use"
    core.check_port.assert_called_once_with("8080")

def test_gui_kill_process(app, qtbot):
    """Test the 'Kill Process' functionality."""
    gui, core = app
    gui.notebook.setCurrentIndex(1)
    
    core.kill_process.return_value = ("Process 1234 terminated", 0)
    
    gui.pid_entry.setText("1234")
    # FIX: Correctly find the button and click.
    kill_button = find_button_by_text(gui.notebook.currentWidget(), "Kill")
    assert kill_button is not None
    qtbot.mouseClick(kill_button, Qt.MouseButton.LeftButton)
    
    assert gui.pm_output_text.toPlainText() == "Process 1234 terminated"
    core.kill_process.assert_called_once_with("1234", confirm=True)

def test_gui_block_port(app, qtbot):
    """Test the 'Block Port' functionality."""
    gui, core = app
    gui.notebook.setCurrentIndex(1)

    core.block_port.return_value = ("Port 5000 Blocked", 0)

    gui.block_port_entry.setText("5000")
    gui.pm_tcp_radio.setChecked(True)
    # FIX: Correctly find the button and click.
    block_button = find_button_by_text(gui.notebook.currentWidget(), "Block")
    assert block_button is not None
    qtbot.mouseClick(block_button, Qt.MouseButton.LeftButton)
    
    assert gui.pm_output_text.toPlainText() == "Port 5000 Blocked"
    core.block_port.assert_called_once_with("5000", "TCP", confirm=True)