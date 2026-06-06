### Imports ###

# Qt imports

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QStackedWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon

# System imports
import sys
from typing import NoReturn
import subprocess
import os

# Local imports
import functions
import plugin_loader
from logger import logger
from update_checker import UpdateChecker

### Main Window Class ###
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.update_checker = UpdateChecker()
        update_check = self.update_checker.check_for_updates()
        if update_check is True:
            app_dir = os.path.dirname(sys.executable)
            subprocess.Popen(["updater.exe", app_dir])
            sys.exit(0)

        self.init_ui()

    def init_ui(self):
        logger.info("Initializing UI")
        self.setWindowTitle('CapyUtilities')
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.show()
        self.setWindowIcon(QIcon(str(functions.resolve_path("icon.ico"))))
        self.setMinimumSize(400, 300)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Create start page
        self.start_page = self.build_start_page()
        self.stack.addWidget(self.start_page)

        logger.info("Loading all plugins...")
        self.plugins = plugin_loader.load_plugins()
        logger.info(f"Loaded all plugins. Plugin names: {[p['name'] for p in self.plugins]}")

    def open_plugin(self, plugin):
        widget_class = plugin["widget"]
        widget = widget_class(go_home_callback=self.go_home)

        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)
        logger.info(f"Opened plugin: {plugin['name']}") # Debug info


    def build_start_page(self):
        logger.info("Creating start page UI...")
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel('CapyUtilities')
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText('Search tools...')
        self.search_bar.setMinimumHeight(40)
        self.search_bar.returnPressed.connect(self.on_run_click)
        layout.addWidget(self.search_bar)

        button_layout = QHBoxLayout()
        self.btn_action = QPushButton('Run Utility')
        self.btn_clear = QPushButton('Clear Search')

        button_layout.addWidget(self.btn_action)
        button_layout.addWidget(self.btn_clear)
        layout.addLayout(button_layout)

        self.btn_action.clicked.connect(self.on_run_click)
        self.btn_clear.clicked.connect(lambda: self.search_bar.clear())

        layout.addStretch()

        logger.info("Start page UI created successfully")
        return widget
    def go_home(self):
        self.stack.setCurrentWidget(self.start_page)

    def on_run_click(self):
        logger.info("User used search bar. Attempting to find plugin...")
        query = self.search_bar.text().lower()

        for plugin in self.plugins:
            if query in plugin["name"].lower() or any(query in k for k in plugin["keywords"]):
                logger.info(f"Plugin matched for query '{query}': {plugin['name']}. Starting plugin...") # Debug info
                self.open_plugin(plugin)
                return

        logger.info(f"No matching utility found for query '{query}'")

def main() -> NoReturn:
    logger.info("Application started runnning...")
    app = QApplication(sys.argv)
    logger.info("QApplication created")

    ## Load Font ##
    try:
        logger.info("Loading custom fonts...")
        # Load both regular and bold
        font_family = functions.load_custom_font("DMSans-Regular.ttf")
        functions.load_custom_font("DMSans-Bold.ttf")

        # Set the global font for the whole app
        app.setFont(QFont(font_family, 11))
        logger.info("Fonts loaded successfully")
        
    except RuntimeError as e:
        logger.error(f"Font loading failed: {e}")

    logger.info("Starting main window...")
    window = MainWindow()
    logger.info("Main window created successfully.")
    window.show()
    logger.debug("Main window shown. Entering application event loop.")
    sys.exit(app.exec())

if __name__ == '__main__':
    logger.info("Starting application...")
    main()