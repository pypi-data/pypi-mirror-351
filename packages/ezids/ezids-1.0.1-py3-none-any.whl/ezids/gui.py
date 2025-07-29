#!/usr/bin/env python3
import sys
import json
import subprocess
import os
import signal
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QTextEdit, QVBoxLayout,
    QHBoxLayout, QStackedLayout, QLineEdit, QListWidget, QInputDialog,
    QFileDialog, QMessageBox, QTabWidget, QFormLayout
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QTextCursor, QIcon
from datetime import datetime
import os

if getattr(sys, 'frozen', False):
    # Running in a PyInstaller bundle
    BASE_DIR = sys._MEIPASS
else:
    # Running as a normal script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def label_with_icon(icon_path, text):
    container = QWidget()
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)

    icon_label = QLabel()
    icon = QIcon(os.path.join(BASE_DIR, icon_path))
    pixmap = icon.pixmap(QSize(16, 16))
    icon_label.setPixmap(pixmap)

    text_label = QLabel(text)
    text_label.setStyleSheet("padding-left: 6px;")

    layout.addWidget(icon_label)
    layout.addWidget(text_label)
    layout.addStretch()

    container.setLayout(layout)
    return container


CONFIG_FILE = "config.json"
PID_FILE = "monitor.pid"

def load_config():
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "monitor_refresh_interval": 30,
            "log_retention_lines": 10000,
            "live_log_lines": 1000,
            "change_log_lines": 5000
        }

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

class IDSMainPage(QWidget):
    def __init__(self, switch_to_settings):
        super().__init__()
        self.switch_to_settings = switch_to_settings
        self.config = load_config()

        self.status_label = QLabel("Status: Idle")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.follow_log = True

        self.live_log = QTextEdit()
        self.live_log.setReadOnly(True)
        self.live_log_label = QLabel()
        self.live_log_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.changes_log = QTextEdit()
        self.changes_log.setReadOnly(True)
        self.change_log_label = QLabel()
        self.change_log_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.follow_checkbox = QPushButton(QIcon(os.path.join(BASE_DIR, "resources", "stop.svg")), "Freeze Scroll")
        self.follow_checkbox.setCheckable(True)
        self.follow_checkbox.setChecked(False)
        self.follow_checkbox.clicked.connect(self.toggle_follow)

        self.init_button = QPushButton(QIcon(os.path.join(BASE_DIR, "resources", "init.svg")), " init")
        self.scan_button = QPushButton(QIcon(os.path.join(BASE_DIR, "resources", "play.svg")), " Scan")
        self.monitor_button = QPushButton(QIcon(os.path.join(BASE_DIR, "resources/eye.svg")), " Monitor")
        self.stop_button = QPushButton(QIcon(os.path.join(BASE_DIR, "resources/eye-off.svg")), " Stop Monitoring")
        self.settings_button = QPushButton(QIcon(os.path.join(BASE_DIR, "resources/settings.svg")), " Settings")

        self.init_button.clicked.connect(self.run_init)
        self.scan_button.clicked.connect(self.run_scan)
        self.monitor_button.clicked.connect(self.run_monitor)
        self.stop_button.clicked.connect(self.stop_monitor)
        self.settings_button.clicked.connect(self.switch_to_settings)

        # Layouts
        button_row = QHBoxLayout()
        button_row.addWidget(self.init_button)
        button_row.addWidget(self.scan_button)
        button_row.addWidget(self.monitor_button)
        button_row.addWidget(self.stop_button)
        button_row.addStretch()
        button_row.addWidget(self.settings_button)

        self.log_tabs = QTabWidget()
        self.log_tabs.addTab(self.live_log, QIcon(os.path.join(BASE_DIR, "resources", "log.svg")), " Live Log")
        self.log_tabs.addTab(self.changes_log, QIcon(os.path.join(BASE_DIR, "resources", "zap.svg")), " Change Events")

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addLayout(button_row)
        layout.addWidget(self.follow_checkbox)
        layout.addWidget(self.log_tabs)
        self.setLayout(layout)

        self.log_timer = QTimer(self)
        self.log_timer.timeout.connect(self.refresh_log)
        self.log_timer.stop()

        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #e0e0e0;
            }
            QIcon {
                color:#ffffff;
            }
            QPushButton {
                font-size: 14px;
                padding: 6px 14px;
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #333;
            }
            QPushButton:hover {
                background-color: #2e2e2e;
            }
            QTextEdit {
                font-family: Consolas, monospace;
                font-size: 12px;
                background-color: #1e1e1e;
                color: #d0d0d0;
                border: 1px solid #444;
            }
            QLabel {
                font-size: 13px;
                color: #e0e0e0;
            }
            QTabWidget::pane {
                border: 1px solid #333;
                background-color: #121212;
            }
            QTabBar::tab {
                background: #1e1e1e;
                color: #ccc;
                padding: 6px;
            }
            QTabBar::tab:selected {
                background: #333;
                color: #fff;
            }
        """)


        self.refresh_log()

    def toggle_follow(self):
        self.follow_log = not self.follow_log
        if self.follow_log:
            self.follow_checkbox.setIcon(QIcon(os.path.join(BASE_DIR, "resources", "stop.svg")))
            self.follow_checkbox.setText(" Freeze Scroll")
        else:
            self.follow_checkbox.setIcon(QIcon(os.path.join(BASE_DIR, "resources", "down.svg")))
            self.follow_checkbox.setText(" Follow Log")


    def run_init(self):
        self.status_label.setText("Creating baseline...")
        subprocess.run([sys.executable, "-m", "ezids.ids_core", "--init"])
        self.status_label.setText("Baseline created.")
        self.refresh_log()

    def run_scan(self):
        self.status_label.setText("Running scan...")
        subprocess.run([sys.executable, "-m", "ezids.ids_core"])
        self.status_label.setText("Scan complete.")
        self.refresh_log()

    def run_monitor(self):
        interval = self.config.get("monitor_refresh_interval", 30)
        self.status_label.setText(f"Monitor mode started (refresh interval: {interval}s)...")
        process = subprocess.Popen([sys.executable, "-m", "ezids.ids_core", "--monitor", "--interval", str(interval)])
        with open(PID_FILE, "w") as f:
            f.write(str(process.pid))
        self.status_label.setText("Monitor mode running.")
        self.log_timer.start(interval * 1000)

    def stop_monitor(self):
        if os.path.exists(PID_FILE):
            with open(PID_FILE) as f:
                pid = int(f.read())
            try:
                os.kill(pid, signal.SIGTERM)
                self.status_label.setText("Monitor mode stopped.")
            except ProcessLookupError:
                self.status_label.setText("Monitor process already stopped.")
            os.remove(PID_FILE)
        else:
            self.status_label.setText("No active monitor process found.")
        self.log_timer.stop()
        self.refresh_log()

    def refresh_log(self):
        def read_tail(file_path, max_lines):
            if not os.path.exists(file_path):
                return []
            with open(file_path) as f:
                return f.readlines()[-max_lines:]

        self.config = load_config()

        # Live log
        live_lines = self.config.get("live_log_lines", 1000)
        lines = read_tail("ids.log", live_lines)

        live_scroll = self.live_log.verticalScrollBar().value()
        self.live_log.setUpdatesEnabled(False)
        self.live_log.clear()
        for line in lines:
            self.append_colored_line(self.live_log, line)
        if self.follow_log:
            self.live_log.moveCursor(QTextCursor.MoveOperation.End)
        else:
            self.live_log.verticalScrollBar().setValue(live_scroll)
        self.live_log.setUpdatesEnabled(True)

        # Change log
        change_lines = self.config.get("change_log_lines", 5000)
        lines = read_tail("ids.log", change_lines)

        change_scroll = self.changes_log.verticalScrollBar().value()
        self.changes_log.setUpdatesEnabled(False)
        self.changes_log.clear()
        for line in lines:
            if any(tag in line for tag in ["File changes detected", "ADDED:", "MODIFIED:", "DELETED:", "[!]"]):
                self.append_colored_line(self.changes_log, line)
        if self.follow_log:
            self.changes_log.moveCursor(QTextCursor.MoveOperation.End)
        else:
            self.changes_log.verticalScrollBar().setValue(change_scroll)
        self.changes_log.setUpdatesEnabled(True)

    def append_colored_line(self, widget, line):
        try:
            timestamp_str, msg = line.split(" - ", 1)
            timestamp = datetime.fromisoformat(timestamp_str)
            ago = int((datetime.now() - timestamp).total_seconds())
            pretty = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            line = f"{pretty}: {ago}s ago - {msg}"
        except:
            pass

        if "File changes detected" in line or "[!]" in line:
            widget.setTextColor(Qt.GlobalColor.red)
        elif "ADDED:" in line:
            widget.setTextColor(Qt.GlobalColor.green)
        elif "MODIFIED:" in line:
            widget.setTextColor(Qt.GlobalColor.blue)
        elif "DELETED:" in line:
            widget.setTextColor(Qt.GlobalColor.darkYellow)
        else:
            widget.setTextColor(Qt.GlobalColor.black)

        widget.append(line)

    def reload_config(self):
        self.config = load_config()
        self.live_log_label.setText(f"Live Log (Latest {self.config.get('live_log_lines', 1000)} lines):")
        self.change_log_label.setText(f"Change Events Only (Latest {self.config.get('change_log_lines', 5000)} lines):")







                    #SETTINGS


class SettingsPage(QWidget):
    def __init__(self, switch_to_main):
        super().__init__()
        self.switch_to_main = switch_to_main
        self.config = load_config()

        self.setStyleSheet("""
            QWidget {
                color: #e0e0e0;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit {
                padding: 4px;
                font-size: 14px;
                width: 100px;
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444;
            }
            QPushButton {
                padding: 6px 12px;
                font-size: 14px;
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #333;
            }
            QPushButton:hover {
                background-color: #2e2e2e;
            }
            QListWidget {
                background-color: #1e1e1e;
                color: #ccc;
                border: 1px solid #444;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        main_layout.setSpacing(15)

        title_widget = QWidget()
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_label = QLabel()
        icon = QIcon(os.path.join(BASE_DIR, "resources", "settings.svg"))
        pixmap = icon.pixmap(QSize(20, 20))
        icon_label.setPixmap(pixmap)

        text_label = QLabel("Settings")
        text_label.setStyleSheet("font-size: 20px; font-weight: bold; padding-left: 2px;")

        title_layout.addWidget(icon_label)
        title_layout.addWidget(text_label)
        title_widget.setLayout(title_layout)

        main_layout.addWidget(title_widget)


        # === Config Options ===
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.interval_input = QLineEdit()
        self.interval_input.setText(str(self.config.get("monitor_refresh_interval", 30)))
        form_layout.addRow(
            label_with_icon("resources/clock.svg", "Monitor Refresh Interval(seconds):"),
            self.interval_input
        )

        self.retention_lines_input = QLineEdit()
        self.retention_lines_input.setText(str(self.config.get("log_retention_lines", 10000)))
        form_layout.addRow(
            label_with_icon("resources/pencil.svg", "Log Retention Limit(lines):"),
            self.retention_lines_input
        )

        self.live_lines_input = QLineEdit()
        self.live_lines_input.setText(str(self.config.get("live_log_lines", 1000)))
        form_layout.addRow(
            label_with_icon("resources/log.svg", "Live Log Display(lines):"),
            self.live_lines_input
        )

        self.change_lines_input = QLineEdit()
        self.change_lines_input.setText(str(self.config.get("change_log_lines", 5000)))
        form_layout.addRow(
            label_with_icon("resources/zap.svg", "Change Log Display(lines):"),
            self.change_lines_input
        )

        main_layout.addLayout(form_layout)

        # === Monitored Paths Section ===
        paths_header = QWidget()
        paths_header_layout = QHBoxLayout()
        paths_header_layout.setContentsMargins(0, 0, 0, 0)
        paths_header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        paths_icon = QLabel()
        icon = QIcon(os.path.join(BASE_DIR, "resources", "folder.svg"))  # update this with the right icon
        pixmap = icon.pixmap(QSize(16, 16))
        paths_icon.setPixmap(pixmap)

        paths_label = QLabel("Monitored Paths:")
        paths_label.setStyleSheet("font-weight: bold; padding-left: 6px;")

        paths_header_layout.addWidget(paths_icon)
        paths_header_layout.addWidget(paths_label)
        paths_header.setLayout(paths_header_layout)

        main_layout.addWidget(paths_header)


        self.paths_list = QListWidget()
        main_layout.addWidget(self.paths_list)

        paths_btns = QHBoxLayout()
        self.add_path_btn = QPushButton(QIcon(os.path.join(BASE_DIR, "resources", "plus.svg")), "Add")
        self.browse_path_btn = QPushButton(QIcon(os.path.join(BASE_DIR, "resources", "file-plus.svg")), "Browse")
        self.remove_path_btn = QPushButton(QIcon(os.path.join(BASE_DIR, "resources", "minus.svg")), "Remove")

        self.add_path_btn.clicked.connect(self.add_path)
        self.browse_path_btn.clicked.connect(self.browse_path)
        self.remove_path_btn.clicked.connect(self.remove_selected_path)

        paths_btns.addWidget(self.add_path_btn)
        paths_btns.addWidget(self.browse_path_btn)
        paths_btns.addWidget(self.remove_path_btn)
        main_layout.addLayout(paths_btns)

        # === Ignored Files Section ===

        paths_header = QWidget()
        paths_header_layout = QHBoxLayout()
        paths_header_layout.setContentsMargins(0, 0, 0, 0)
        paths_header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        paths_icon = QLabel()
        icon = QIcon(os.path.join(BASE_DIR, "resources", "slash.svg"))  # update this with the right icon
        pixmap = icon.pixmap(QSize(16, 16))
        paths_icon.setPixmap(pixmap)

        paths_label = QLabel("Ignored Files:")
        paths_label.setStyleSheet("font-weight: bold; padding-left: 6px;")

        paths_header_layout.addWidget(paths_icon)
        paths_header_layout.addWidget(paths_label)
        paths_header.setLayout(paths_header_layout)

        main_layout.addWidget(paths_header)

        self.ignore_list = QListWidget()
        main_layout.addWidget(self.ignore_list)




        ignore_btns = QHBoxLayout()
        self.add_ignore_btn = QPushButton(QIcon(os.path.join(BASE_DIR, "resources", "plus.svg")), "Add")
        self.browse_ignore_btn = QPushButton(QIcon(os.path.join(BASE_DIR, "resources", "file-plus.svg")), "Browse")
        self.remove_ignore_btn = QPushButton(QIcon(os.path.join(BASE_DIR, "resources", "minus.svg")), "Remove")

        self.add_ignore_btn.clicked.connect(self.add_ignore)
        self.browse_ignore_btn.clicked.connect(self.browse_ignore)
        self.remove_ignore_btn.clicked.connect(self.remove_selected_ignore)

        ignore_btns.addWidget(self.add_ignore_btn)
        ignore_btns.addWidget(self.browse_ignore_btn)
        ignore_btns.addWidget(self.remove_ignore_btn)
        main_layout.addLayout(ignore_btns)

        # === Bottom Buttons ===
        nav_btns = QHBoxLayout()
        self.save_btn = QPushButton(QIcon(os.path.join(BASE_DIR, "resources", "save.svg")), "Save")
        self.back_btn = QPushButton(QIcon(os.path.join(BASE_DIR, "resources", "back.svg")), "Back")
        self.save_btn.clicked.connect(self.save_settings)
        self.back_btn.clicked.connect(self.switch_to_main)
        nav_btns.addWidget(self.save_btn)
        nav_btns.addWidget(self.back_btn)
        main_layout.addLayout(nav_btns)

        self.setLayout(main_layout)

    def load_monitor_paths(self):
        self.paths_list.clear()
        if not os.path.exists("monitor_paths.txt"):
            return
        with open("monitor_paths.txt") as f:
            for line in f:
                path = line.strip()
                if path and not path.startswith("#"):
                    self.paths_list.addItem(path)

    def save_monitor_paths(self):
        paths = [self.paths_list.item(i).text() for i in range(self.paths_list.count())]
        with open("monitor_paths.txt", "w") as f:
            for p in paths:
                f.write(p.strip() + "\n")

    def add_path(self):
        path, ok = QInputDialog.getText(self, "Add Path", "Enter a path to monitor:")
        if ok and path.strip():
            self.paths_list.addItem(path.strip())

    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Directory to Monitor")
        if path:
            self.paths_list.addItem(path)

    def remove_selected_path(self):
        for item in self.paths_list.selectedItems():
            self.paths_list.takeItem(self.paths_list.row(item))


    def load_ignore_paths(self):
        self.ignore_list.clear()
        if not os.path.exists("ignore_files.txt"):
            return
        with open("ignore_files.txt") as f:
            for line in f:
                path = line.strip()
                if path and not path.startswith("#"):
                    self.ignore_list.addItem(path)

    def save_ignore_paths(self):
        paths = [self.ignore_list.item(i).text() for i in range(self.ignore_list.count())]
        with open("ignore_files.txt", "w") as f:
            for p in paths:
                f.write(p.strip() + "\n")

    def add_ignore(self):
        path, ok = QInputDialog.getText(self, "Add Ignore Path", "Enter file path to ignore:")
        if ok and path.strip():
            self.ignore_list.addItem(path.strip())

    def browse_ignore(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select File to Ignore")
        if path:
            self.ignore_list.addItem(path)

    def remove_selected_ignore(self):
        for item in self.ignore_list.selectedItems():
            self.ignore_list.takeItem(self.ignore_list.row(item))



    def save_settings(self):
        try:
            interval = int(self.interval_input.text())
            retention_lines = int(self.retention_lines_input.text())
            self.config["log_retention_lines"] = retention_lines

            live_lines = int(self.live_lines_input.text())
            self.config["live_log_lines"] = live_lines

            self.config["monitor_refresh_interval"] = interval

            change_lines = int(self.change_lines_input.text())
            self.config["change_log_lines"] = change_lines

            save_config(self.config)


            self.save_monitor_paths()
            self.save_ignore_paths()
            QMessageBox.information(self, "Settings Saved", "Configuration updated successfully.")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numbers for interval and max log lines.")



class IDSApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EZIDS — Intrusion Detection System")
        self.resize(600, 400)

        self.stack = QStackedLayout()

        self.main_page = IDSMainPage(self.show_settings)
        self.settings_page = SettingsPage(self.show_main)

        self.stack.addWidget(self.main_page)
        self.stack.addWidget(self.settings_page)

        self.setLayout(self.stack)

    def show_settings(self):
        self.settings_page.load_monitor_paths()
        self.settings_page.load_ignore_paths()
        self.stack.setCurrentWidget(self.settings_page)


    def show_main(self):
        self.main_page.reload_config()
        self.stack.setCurrentWidget(self.main_page)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IDSApp()
    window.show()
    sys.exit(app.exec())
