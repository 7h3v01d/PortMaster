import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QGroupBox, QLabel, QLineEdit, QPushButton, QRadioButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from core import PortManagerCore

class PortManagerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.core = PortManagerCore()
        self.setWindowTitle("Portmaster - Network Management (PyQt6)")
        self.setGeometry(100, 100, 1100, 750)  # Set a good default size

        # Main container widget
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)

        # Tabbed interface
        self.notebook = QTabWidget()
        self.main_layout.addWidget(self.notebook)

        # Create and add tabs
        self.setup_connections_tab()
        self.setup_port_management_tab()
        self.setup_server_tab()
        self.setup_reservations_tab()

    # ======================================================================
    # Connections Tab
    # ======================================================================
    def setup_connections_tab(self):
        """Connections tab: List connections in a sortable table and save to file"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.notebook.addTab(tab, "Connections")

        # --- Controls Group ---
        controls_group = QGroupBox()
        controls_layout = QHBoxLayout(controls_group)
        layout.addWidget(controls_group)

        list_btn = QPushButton("List Connections")
        list_btn.clicked.connect(self.list_connections)
        controls_layout.addWidget(list_btn)

        controls_layout.addStretch(1) # Pushes the save controls to the right

        save_label = QLabel("File Path:")
        self.save_file_entry = QLineEdit(r"E:\S.I.M.O.N\thalamus\portmaster\output.txt")
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_connections)
        
        controls_layout.addWidget(save_label)
        controls_layout.addWidget(self.save_file_entry)
        controls_layout.addWidget(save_btn)

        # --- Table for Connections Display ---
        self.connections_table = QTableWidget()
        self.connections_table.setColumnCount(6)
        self.connections_table.setHorizontalHeaderLabels([
            "Protocol", "Local Address", "Remote Address", "Status", "PID", "Process Name"
        ])
        self.connections_table.setSortingEnabled(True)
        self.connections_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Read-only
        self.connections_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.connections_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.connections_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents) # Process name
        layout.addWidget(self.connections_table)

    # ======================================================================
    # Port Management Tab
    # ======================================================================
    def setup_port_management_tab(self):
        """Port Management tab: Check port, kill process, block/unblock port"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        self.notebook.addTab(tab, "Port Management")

        # --- Controls Container ---
        controls_container = QWidget()
        controls_layout = QVBoxLayout(controls_container)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(controls_container)

        # Check Port
        check_group = QGroupBox("Check Port")
        check_layout = QHBoxLayout(check_group)
        self.port_entry = QLineEdit()
        self.port_entry.setPlaceholderText("Port")
        check_btn = QPushButton("Check")
        check_btn.clicked.connect(self.check_port)
        check_layout.addWidget(QLabel("Port:"))
        check_layout.addWidget(self.port_entry)
        check_layout.addWidget(check_btn)
        controls_layout.addWidget(check_group)

        # Kill Process
        kill_group = QGroupBox("Kill Process")
        kill_layout = QHBoxLayout(kill_group)
        self.pid_entry = QLineEdit()
        self.pid_entry.setPlaceholderText("PID")
        kill_btn = QPushButton("Kill")
        kill_btn.clicked.connect(self.kill_process)
        kill_layout.addWidget(QLabel("PID:"))
        kill_layout.addWidget(self.pid_entry)
        kill_layout.addWidget(kill_btn)
        controls_layout.addWidget(kill_group)

        # Block/Unblock Port
        block_group = QGroupBox("Block/Unblock Port")
        block_layout = QGridLayout(block_group)
        self.block_port_entry = QLineEdit()
        self.block_port_entry.setPlaceholderText("Port")
        self.pm_tcp_radio = QRadioButton("TCP")
        self.pm_udp_radio = QRadioButton("UDP")
        self.pm_tcp_radio.setChecked(True)
        block_btn = QPushButton("Block")
        unblock_btn = QPushButton("Unblock")
        block_btn.clicked.connect(self.block_port)
        unblock_btn.clicked.connect(self.unblock_port)
        block_layout.addWidget(QLabel("Port:"), 0, 0)
        block_layout.addWidget(self.block_port_entry, 0, 1, 1, 2)
        block_layout.addWidget(self.pm_tcp_radio, 1, 1)
        block_layout.addWidget(self.pm_udp_radio, 1, 2)
        block_layout.addWidget(block_btn, 2, 1)
        block_layout.addWidget(unblock_btn, 2, 2)
        controls_layout.addWidget(block_group)
        
        # --- Output Area ---
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)
        self.pm_output_text = QTextEdit()
        self.pm_output_text.setReadOnly(True)
        output_layout.addWidget(self.pm_output_text)
        layout.addWidget(output_group, 1) # Set stretch factor to take more space

    # ======================================================================
    # Server Tab
    # ======================================================================
    def setup_server_tab(self):
        """Server tab: Start/stop server"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        self.notebook.addTab(tab, "Server")
        
        # --- Controls Container ---
        controls_container = QWidget()
        controls_layout = QVBoxLayout(controls_container)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(controls_container)
        
        server_group = QGroupBox("Server Control")
        server_layout = QGridLayout(server_group)
        self.server_port_entry = QLineEdit()
        self.server_port_entry.setPlaceholderText("Port")
        self.server_tcp_radio = QRadioButton("TCP")
        self.server_udp_radio = QRadioButton("UDP")
        self.server_tcp_radio.setChecked(True)
        start_btn = QPushButton("Start Server")
        stop_btn = QPushButton("Stop Server")
        start_btn.clicked.connect(self.start_server)
        stop_btn.clicked.connect(self.stop_server)
        
        server_layout.addWidget(QLabel("Port:"), 0, 0)
        server_layout.addWidget(self.server_port_entry, 0, 1, 1, 2)
        server_layout.addWidget(self.server_tcp_radio, 1, 1)
        server_layout.addWidget(self.server_udp_radio, 1, 2)
        server_layout.addWidget(start_btn, 2, 1)
        server_layout.addWidget(stop_btn, 2, 2)
        controls_layout.addWidget(server_group)

        # --- Output Area ---
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)
        self.server_output_text = QTextEdit()
        self.server_output_text.setReadOnly(True)
        output_layout.addWidget(self.server_output_text)
        layout.addWidget(output_group, 1)

    # ======================================================================
    # Reservations Tab
    # ======================================================================
    def setup_reservations_tab(self):
        """Reservations tab: Reserve/release port"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        self.notebook.addTab(tab, "Reservations")

        # --- Controls Container ---
        controls_container = QWidget()
        controls_layout = QVBoxLayout(controls_container)
        controls_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(controls_container)
        
        reserve_group = QGroupBox("Port Reservation")
        reserve_layout = QGridLayout(reserve_group)
        self.reserve_port_entry = QLineEdit()
        self.reserve_port_entry.setPlaceholderText("Port")
        self.reserve_tcp_radio = QRadioButton("TCP")
        self.reserve_udp_radio = QRadioButton("UDP")
        self.reserve_tcp_radio.setChecked(True)
        self.exe_path_entry = QLineEdit(r"C:\Windows\notepad.exe")
        reserve_btn = QPushButton("Reserve")
        release_btn = QPushButton("Release")
        reserve_btn.clicked.connect(self.reserve_port)
        release_btn.clicked.connect(self.release_port)
        
        reserve_layout.addWidget(QLabel("Port:"), 0, 0)
        reserve_layout.addWidget(self.reserve_port_entry, 0, 1, 1, 2)
        reserve_layout.addWidget(self.reserve_tcp_radio, 1, 1)
        reserve_layout.addWidget(self.reserve_udp_radio, 1, 2)
        reserve_layout.addWidget(QLabel("Exe Path:"), 2, 0)
        reserve_layout.addWidget(self.exe_path_entry, 2, 1, 1, 2)
        reserve_layout.addWidget(reserve_btn, 3, 1)
        reserve_layout.addWidget(release_btn, 3, 2)
        controls_layout.addWidget(reserve_group)

        # --- Output Area ---
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)
        self.res_output_text = QTextEdit()
        self.res_output_text.setReadOnly(True)
        output_layout.addWidget(self.res_output_text)
        layout.addWidget(output_group, 1)

    # ======================================================================
    # Backend Logic Methods (Slots)
    # ======================================================================
    def _confirm_action(self, title, message):
        """Helper to show a confirmation dialog."""
        reply = QMessageBox.question(self, title, message,
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        return reply == QMessageBox.StandardButton.Yes

    def list_connections(self):
        try:
            connections = self.core.list_connections()
            self.connections_table.setRowCount(0) # Clear table
            for row, conn in enumerate(connections):
                self.connections_table.insertRow(row)
                for col, value in enumerate(conn.values()):
                    item = QTableWidgetItem(str(value))
                    # For numeric columns, set data for proper sorting
                    if col == 4: # PID column
                        item.setData(Qt.ItemDataRole.DisplayRole, int(value))
                    self.connections_table.setItem(row, col, item)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to list connections: {str(e)}")

    def check_port(self):
        port = self.port_entry.text()
        if not port:
            QMessageBox.warning(self, "Input Error", "Please enter a port number")
            return
        output, rc = self.core.check_port(port)
        self.pm_output_text.setText(output)
        if rc != 0:
            QMessageBox.critical(self, "Error", output)

    def kill_process(self):
        pid = self.pid_entry.text()
        if not pid:
            QMessageBox.warning(self, "Input Error", "Please enter a PID")
            return
        if self._confirm_action("Confirm Kill", f"Are you sure you want to terminate PID {pid}?"):
            output, rc = self.core.kill_process(pid, confirm=True)
            self.pm_output_text.setText(output)
            if rc != 0:
                QMessageBox.critical(self, "Error", output)

    def block_port(self):
        port = self.block_port_entry.text()
        protocol = "TCP" if self.pm_tcp_radio.isChecked() else "UDP"
        if not port:
            QMessageBox.warning(self, "Input Error", "Please enter a port number")
            return
        if self._confirm_action("Confirm Block", f"Are you sure you want to block {protocol} port {port}?"):
            output, rc = self.core.block_port(port, protocol, confirm=True)
            self.pm_output_text.setText(output)
            if rc != 0:
                QMessageBox.critical(self, "Error", output)

    def unblock_port(self):
        port = self.block_port_entry.text()
        protocol = "TCP" if self.pm_tcp_radio.isChecked() else "UDP"
        if not port:
            QMessageBox.warning(self, "Input Error", "Please enter a port number")
            return
        if self._confirm_action("Confirm Unblock", f"Are you sure you want to unblock {protocol} port {port}?"):
            output, rc = self.core.unblock_port(port, protocol, confirm=True)
            self.pm_output_text.setText(output)
            if rc != 0:
                QMessageBox.critical(self, "Error", output)

    def start_server(self):
        port = self.server_port_entry.text()
        protocol = "TCP" if self.server_tcp_radio.isChecked() else "UDP"
        if not port:
            QMessageBox.warning(self, "Input Error", "Please enter a port number")
            return
        if self._confirm_action("Confirm Start", f"Are you sure you want to start a server on {protocol} port {port}?"):
            output, rc = self.core.start_server(port, protocol, confirm=True)
            self.server_output_text.setText(output)
            if rc != 0:
                QMessageBox.critical(self, "Error", output)

    def stop_server(self):
        if self._confirm_action("Confirm Stop", "Are you sure you want to stop the running server?"):
            output, rc = self.core.stop_server(confirm=True)
            self.server_output_text.setText(output)
            if rc != 0:
                QMessageBox.critical(self, "Error", output)

    def reserve_port(self):
        port = self.reserve_port_entry.text()
        protocol = "TCP" if self.reserve_tcp_radio.isChecked() else "UDP"
        exe_path = self.exe_path_entry.text()
        if not port or not exe_path:
            QMessageBox.warning(self, "Input Error", "Please enter a port number and an executable path")
            return
        if self._confirm_action("Confirm Reserve", f"Reserve {protocol} port {port} for {exe_path}?"):
            output, rc = self.core.reserve_port(port, protocol, exe_path, confirm=True)
            self.res_output_text.setText(output)
            if rc != 0:
                QMessageBox.critical(self, "Error", output)

    def release_port(self):
        port = self.reserve_port_entry.text()
        if not port:
            QMessageBox.warning(self, "Input Error", "Please enter a port number")
            return
        if self._confirm_action("Confirm Release", f"Are you sure you want to release port {port}?"):
            output, rc = self.core.release_port(port, confirm=True)
            self.res_output_text.setText(output)
            if rc != 0:
                QMessageBox.critical(self, "Error", output)

    def save_connections(self):
        filename = self.save_file_entry.text()
        if not filename:
            QMessageBox.warning(self, "Input Error", "Please enter a file path")
            return
        try:
            output, rc = self.core.save_connections(filename)
            if rc == 0:
                QMessageBox.information(self, "Success", output)
            else:
                QMessageBox.critical(self, "Error", output)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PortManagerGUI()
    window.show()
    sys.exit(app.exec())