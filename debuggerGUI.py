import sys
import json
import threading
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QListWidget, QListWidgetItem, QSplitter, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer
from PyQt5.QtGui import QTextCursor, QColor, QFont

# Assume BF16Client is available from bf16module.utilities.debugger.debugger
# For this example, we'll mock it if not found
try:
    from bf16module.utilities.debugger.debugger import BF16Client
except ImportError:
    print("BF16Client not found, mocking it for GUI demonstration.")
    class BF16Client:
        def __init__(self, host, port):
            self.host = host
            self.port = port
            self._connected = False
            self._mock_data = [
                '{"ID": "instruction_1", "name": "instruction", "data": "PC=0 CMD=>"}',
                '{"ID": "pointer_1", "name": "pointer", "data": "> Move right by 1 → 1"}',
                '{"ID": "instruction_2", "name": "instruction", "data": "PC=2 CMD=+"}',
                '{"ID": "memory_2", "name": "memory", "data": "+ Add 1 → mem[1] 0 → 1"}',
                '{"ID": "instruction_3", "name": "instruction", "data": "PC=4 CMD=."}',
                '{"ID": "render_3", "name": "render", "data": "Display frame updated"}',
                '{"ID": "program_end_4", "name": "program_end", "data": "Program finished"}'
            ]
            self._data_index = 0

        def connect(self):
            print(f"Mock: Connecting to {self.host}:{self.port}")
            self._connected = True
            return True

        def send_data(self, data):
            print(f"Mock: Sending data: {data}")

        def receive_data(self):
            if not self._connected:
                return None
            if self._data_index < len(self._mock_data):
                data = self._mock_data[self._data_index]
                self._data_index += 1
                time.sleep(0.1) # Simulate network delay
                return data
            return None

        def close(self):
            print("Mock: Closing connection")
            self._connected = False

class DebuggerSignals(QObject):
    data_received = pyqtSignal(str)
    connection_status_changed = pyqtSignal(bool)

class DebuggerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.client = None
        self.signals = DebuggerSignals()
        self.signals.data_received.connect(self.handle_data_received)
        self.signals.connection_status_changed.connect(self.update_connection_status)
        self.data_receive_thread = None
        self.is_receiving_data = False
        self.init_ui()
        self.memory_data = {} # To store memory values

    def init_ui(self):
        self.setWindowTitle("BF16 Debugger")
        self.setGeometry(100, 100, 1200, 800)

        # Main layout
        main_layout = QVBoxLayout()

        # Connection controls
        connection_layout = QHBoxLayout()
        self.host_input = QLineEdit("127.0.0.1")
        self.host_input.setPlaceholderText("Host")
        self.port_input = QLineEdit("5000")
        self.port_input.setPlaceholderText("Port")
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_server)
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.clicked.connect(self.disconnect_from_server)
        self.disconnect_button.setEnabled(False)
        self.status_label = QLabel("Status: Disconnected")
        self.status_label.setStyleSheet("color: red")

        connection_layout.addWidget(QLabel("Host:"))
        connection_layout.addWidget(self.host_input)
        connection_layout.addWidget(QLabel("Port:"))
        connection_layout.addWidget(self.port_input)
        connection_layout.addWidget(self.connect_button)
        connection_layout.addWidget(self.disconnect_button)
        connection_layout.addStretch()
        connection_layout.addWidget(self.status_label)
        main_layout.addLayout(connection_layout)

        # Splitter for logs/events and memory/details
        splitter_main = QSplitter(Qt.Horizontal)

        # Left pane: Logs/Events
        left_pane = QWidget()
        left_layout = QVBoxLayout()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Consolas", 10))
        left_layout.addWidget(QLabel("Debugger Log:"))
        left_layout.addWidget(self.log_output)
        left_pane.setLayout(left_layout)
        splitter_main.addWidget(left_pane)

        # Right pane: Memory and Details
        right_pane = QWidget()
        right_layout = QVBoxLayout()

        # Memory Table
        self.memory_table = QTableWidget(16, 16) # 16x16 grid for display
        self.memory_table.setHorizontalHeaderLabels([str(i) for i in range(16)])
        self.memory_table.setVerticalHeaderLabels([str(i) for i in range(16)])
        self.memory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.memory_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.memory_table.setEditTriggers(QTableWidget.NoEditTriggers) # Make it read-only
        right_layout.addWidget(QLabel("Memory (16x16 Display):"))
        right_layout.addWidget(self.memory_table)

        # Details/Event List
        self.event_list = QListWidget()
        right_layout.addWidget(QLabel("Events:"))
        right_layout.addWidget(self.event_list)
        right_pane.setLayout(right_layout)
        splitter_main.addWidget(right_pane)

        splitter_main.setSizes([800, 400]) # Initial sizes for the split panes
        main_layout.addWidget(splitter_main)

        self.setLayout(main_layout)

        # Initialize memory table with zeros
        for i in range(16):
            for j in range(16):
                item = QTableWidgetItem("0")
                item.setTextAlignment(Qt.AlignCenter)
                self.memory_table.setItem(i, j, item)

    def connect_to_server(self):
        host = self.host_input.text()
        port = int(self.port_input.text())
        self.client = BF16Client(host, port)
        if self.client.connect():
            self.signals.connection_status_changed.emit(True)
            self.start_data_reception()
        else:
            self.signals.connection_status_changed.emit(False)

    def disconnect_from_server(self):
        if self.client:
            self.stop_data_reception()
            self.client.close()
            self.client = None
        self.signals.connection_status_changed.emit(False)

    def update_connection_status(self, connected: bool):
        if connected:
            self.status_label.setText("Status: Connected")
            self.status_label.setStyleSheet("color: green")
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
            self.host_input.setEnabled(False)
            self.port_input.setEnabled(False)
            self.log_output.append("--- Connected to debugger server ---")
        else:
            self.status_label.setText("Status: Disconnected")
            self.status_label.setStyleSheet("color: red")
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)
            self.host_input.setEnabled(True)
            self.port_input.setEnabled(True)
            self.log_output.append("--- Disconnected from debugger server ---")

    def start_data_reception(self):
        self.is_receiving_data = True
        self.data_receive_thread = threading.Thread(target=self._receive_data_loop, daemon=True)
        self.data_receive_thread.start()

    def stop_data_reception(self):
        self.is_receiving_data = False
        if self.data_receive_thread and self.data_receive_thread.is_alive():
            self.data_receive_thread.join(timeout=1) # Give it a moment to stop

    def _receive_data_loop(self):
        while self.is_receiving_data and self.client:
            try:
                data = self.client.receive_data()
                if data:
                    self.signals.data_received.emit(data)
                else:
                    # If no data and not explicitly disconnected, assume server closed
                    if self.is_receiving_data:
                        print("Server closed connection or no data received.")
                        self.signals.connection_status_changed.emit(False)
                        self.is_receiving_data = False # Stop the loop
            except Exception as e:
                print(f"Error in data reception loop: {e}")
                self.signals.connection_status_changed.emit(False)
                self.is_receiving_data = False # Stop the loop
            time.sleep(0.01) # Small delay to prevent busy-waiting

    def handle_data_received(self, raw_data: str):
        try:
            # Attempt to parse as JSON
            data = json.loads(raw_data)
            name = data.get("name")
            content = data.get("data")

            # Handle specific event types
            if name == "render":
                if isinstance(content, list) and len(content) == 16 and all(isinstance(row, list) and len(row) == 16 for row in content):
                    # Update the 16x16 memory display
                    for r_idx, row_data in enumerate(content):
                        for c_idx, cell_value in enumerate(row_data):
                            item = self.memory_table.item(r_idx, c_idx)
                            item.setText(str(cell_value))
                else:
                    self.log_output.append(f"<span style='color: orange;'>Warning: 'render' data not in expected 16x16 list format.</span>")

            elif name == "memory":
                # Example: "+ Add 1 → mem[1] 0 → 1"
                # Parse the memory update from the 'data' string
                try:
                    parts = content.split("→ mem[")
                    if len(parts) > 1:
                        addr_val_part = parts[1].split("] ")
                        address = int(addr_val_part[0])
                        new_value = int(addr_val_part[1].split(" → ")[1])
                        self.memory_data[address] = new_value

                        # If this memory address is part of the 16x16 display
                        if 0 <= address < 256:
                            row = address // 16
                            col = address % 16
                            item = self.memory_table.item(row, col)
                            if item:
                                item.setText(str(new_value))
                                intensity = min(255, new_value * 4)
                                color = QColor(intensity, intensity, intensity)
                                item.setBackground(color)
                            else:
                                item = QTableWidgetItem(str(new_value))
                                item.setTextAlignment(Qt.AlignCenter)
                                self.memory_table.setItem(row, col, item)
                except Exception as e:
                    self.log_output.append(f"<span style='color: red;'>Error parsing memory event: {e}</span>")

        except json.JSONDecodeError as e:
            self.log_output.append(f"<span style='color: red;'>Error processing data: {e} </span>")
        except Exception as e:
            self.log_output.append(f"<span style='color: red;'>Error processing data: {e}</span>")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    debugger_gui = DebuggerGUI()
    debugger_gui.show()
    sys.exit(app.exec_())