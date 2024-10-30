import sys
from datetime import datetime

from PySide6.QtCore import QSize, Qt, QDir
from PySide6.QtGui import QAction, QIcon, QKeySequence, QPalette, QColor
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QLabel,
    QMainWindow,
    QStatusBar,
    QToolBar, QFrame, QSizePolicy, QHBoxLayout, QSplitter, QVBoxLayout, QWidget, QFileSystemModel, QTreeView, QTextEdit,
    QPushButton, QScrollArea,
)

from diffs import build_diff_lines
from editor import MyEditor
from syntax_highliting import PythonHighlighter


class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

        self.mode = "file"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1920, 1080)
        self.setStyleSheet(open("styles/main.qss", "r").read())
        self.editor_original = None
        self.editor_ai = None
        self.original_text = ""
        self.ai_text = ""


        self.create_main_content()



    def create_main_content(self):

        main_layout = QVBoxLayout()


        horizontal_widget = QWidget()
        horizontal_layout = QHBoxLayout()
        horizontal_widget.setLayout(horizontal_layout)
        main_layout.addWidget(horizontal_widget)


        main_widget = QWidget()
        main_widget.setLayout(main_layout)



        self.editor_original = MyEditor()
        self.editor_ai = MyEditor()
        highlighter_original = PythonHighlighter(self.editor_original.document())
        highlighter_ai = PythonHighlighter(self.editor_ai.document())

        print(self.original_text)
        if self.original_text:
            self.editor_original.setPlainText(self.original_text)

        if self.ai_text:
            self.editor_ai.setPlainText(self.ai_text)


        self.editor_ai.focus_on_line(90)


        horizontal_layout.addWidget(self.editor_original)
        horizontal_layout.addWidget(self.editor_ai)

        btn = QPushButton("Analyze code")
        btn.setStyleSheet(self.btn_style_main)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedWidth(300)

        btn.clicked.connect(self.the_analyze_button_was_clicked)
        main_layout.addWidget(btn, alignment=Qt.AlignHCenter)

        self.setCentralWidget(main_widget)

    def the_back_button_was_clicked(self, s):
        self.create_main_content()

    def the_analyze_button_was_clicked(self, s):
        self.original_text = self.editor_original.toPlainText()

        self.ai_text = self.editor_ai.toPlainText()
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Create a QVBoxLayout for the main widget
        main_layout = QVBoxLayout()

        # Create a widget to hold the content for the scroll area
        content_widget = QWidget()
        content_widget.setStyleSheet("""
                QWidget {
                    background: #F0EDCC;
                    color: #02343F;
                    border-radius: 10px;
                    padding: 10px;
                }
                
                QLabel {
                padding: 0px;
                }
        """)

        # Create a QVBoxLayout for the scrollable content
        content_layout = QVBoxLayout()
        content_layout.setAlignment(Qt.AlignTop)
        content_layout.setSpacing(0)

        # Add multiple buttons or any content to demonstrate scrolling
        for block in build_diff_lines(
                self.editor_original.toPlainText(), self.editor_ai.toPlainText()
        ):
            content_layout.addWidget(block)

        # Set the layout for the content widget
        content_widget.setLayout(content_layout)

        # Create a QScrollArea and set content widget as its child
        scroll_area = QScrollArea()
        scroll_area.setWidget(content_widget)
        scroll_area.setWidgetResizable(True)  # Ensure it resizes properly with content

        # Set the height of the scroll area to be the window height minus 300px
        scroll_area.setFixedHeight(self.height() - 200)

        # Add the scroll area to the main layout
        main_layout.addWidget(scroll_area)

        # Create a fixed button under the scroll area
        back_button = QPushButton("Go Back")
        back_button.setStyleSheet(self.btn_style_main)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.setFixedWidth(200)

        back_button.clicked.connect(self.the_back_button_was_clicked)
        main_layout.addWidget(back_button, alignment=Qt.AlignHCenter)

        main_widget.setLayout(main_layout)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Adjust the height of the scroll area dynamically
        if self.centralWidget().findChild(QScrollArea):
            self.centralWidget().findChild(QScrollArea).setFixedHeight(self.height() - 200)

    @property
    def btn_style_main(self):
        return """
        QPushButton {
                background: #F0EDCC;
                color: #02343F;
                border: 1px solid black; 
                border-radius: 10px;
                padding: 10px;
                font: bold 15px;
                cursor: pointer;
        }
        QPushButton:hover {
            background: #dedcc3;
        }
        """


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()