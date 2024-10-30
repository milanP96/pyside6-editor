import sys
import difflib
from dataclasses import dataclass
from PySide6.QtCore import QSize, Qt, QModelIndex, QAbstractListModel
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QListView,
)

from editor import MyEditor


@dataclass
class LineData:
    text: str
    line_num: int
    action: str


@dataclass
class BlockData:
    lines: list[LineData]
    action: str


class StringListModel(QAbstractListModel):
    def __init__(self, items=None):
        super().__init__()
        self._items = items or []

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        line_data = self._items[index.row()]

        if role == Qt.DisplayRole:
            return f"{line_data.line_num}     {line_data.text.strip()}"

        if role == Qt.BackgroundRole:
            if line_data.action == "added":
                return QColor("#c3e6ac")
            elif line_data.action == "deleted":
                return QColor("#eda39f")

        return None

    def rowCount(self, parent=QModelIndex()):
        return len(self._items)

    def set_items(self, items):
        self.beginResetModel()
        self._items = items
        self.endResetModel()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1920, 1080)
        self.setStyleSheet(open("styles/main.qss", "r").read())

        self.editor_original = MyEditor()
        self.editor_ai = MyEditor()
        self.original_text = ""
        self.ai_text = ""
        self.create_main_content()

    def create_main_content(self):
        main_layout = QVBoxLayout()
        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        horizontal_layout = QVBoxLayout()

        self.editor_original = MyEditor()
        self.editor_ai = MyEditor()
        self.editor_original.setPlainText(self.original_text)
        self.editor_ai.setPlainText(self.ai_text)

        horizontal_layout.addWidget(self.editor_original)
        horizontal_layout.addWidget(self.editor_ai)

        btn = QPushButton("Analyze code")
        btn.setStyleSheet(self.btn_style_main)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(self.the_analyze_button_was_clicked)

        main_layout.addLayout(horizontal_layout)
        main_layout.addWidget(btn)

        self.setCentralWidget(main_widget)

    def the_analyze_button_was_clicked(self):
        self.original_text = self.editor_original.toPlainText()
        self.ai_text = self.editor_ai.toPlainText()

        self.display_diff_view()

    def display_diff_view(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        self.original_text = self.editor_original.toPlainText()
        self.ai_text = self.editor_ai.toPlainText()

        main_layout = QVBoxLayout()

        self.diff_list_view = QListView()
        self.diff_list_view.setStyleSheet("""
        QListView { background-color: #F0EDCC;}
        """)
        self.model = StringListModel()
        self.diff_list_view.setModel(self.model)

        main_layout.addWidget(self.diff_list_view)

        lines = self.build_diff_lines(self.original_text, self.ai_text)
        self.model.set_items(lines)

        back_button = QPushButton("Go Back")
        back_button.setStyleSheet(self.btn_style_main)
        back_button.setCursor(Qt.PointingHandCursor)
        back_button.clicked.connect(self.go_back_to_editors)

        main_layout.addWidget(back_button)
        main_widget.setLayout(main_layout)

    def go_back_to_editors(self):
        self.create_main_content()

    def build_diff_lines(self, original: str, ai: str):
        blocks = analyze_diff(original, ai)
        lines = []

        for block in blocks:
            for line in block.lines:
                lines.append(LineData(text=line.text, line_num=line.line_num, action=block.action))

        return lines

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


def analyze_diff(file1: str, file2: str):
    lines1 = file1.splitlines(keepends=True)
    lines2 = file2.splitlines(keepends=True)
    diff = difflib.ndiff(lines1, lines2)

    result = []
    current_block = BlockData(lines=[], action=None)

    line_num1 = 1
    line_num2 = 1

    def add_block():
        if current_block.lines:
            result.append(BlockData(lines=current_block.lines.copy(), action=current_block.action))

    for line in diff:
        code, content = line[0], line[2:]

        if code == '-':
            if current_block.action != "deleted":
                add_block()
                current_block = BlockData(lines=[], action="deleted")
            current_block.lines.append(LineData(text=content, line_num=line_num1, action=current_block.action))
            line_num1 += 1

        elif code == '+':
            if current_block.action != "added":
                add_block()
                current_block = BlockData(lines=[], action="added")
            current_block.lines.append(LineData(text=content, line_num=line_num2, action=current_block.action))
            line_num2 += 1

        elif code == ' ':
            if current_block.action != "none":
                add_block()
                current_block = BlockData(lines=[], action="none")
            current_block.lines.append(LineData(text=content, line_num=line_num1, action=current_block.action))
            line_num1 += 1
            line_num2 += 1

    add_block()
    return result


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()
