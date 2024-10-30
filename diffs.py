import difflib
from dataclasses import dataclass

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout
from PySide6.QtCore import QSize, Qt, QDir

@dataclass
class LineData:
    text: str
    line_num: int


@dataclass
class BlockData:
    lines: list[LineData]
    action: str


class Line(QWidget):
    def __init__(self, data: LineData, action: str):
        super().__init__()
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignLeft)
        layout.setAlignment(Qt.AlignVCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)


        num_ = QLabel(data.line_num.__str__())
        num_.setFixedWidth(40)
        num_.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        layout.addWidget(num_)


        self.setFixedHeight(15)
        content = QLabel(data.text)
        content.setAlignment(Qt.AlignVCenter)
        content.setFixedHeight(15)

        layout.addWidget(content)
        self.setLayout(layout)


        # self.setStyle('padding: 1px;')
        if action == 'added':
            self.setStyleSheet("""
            QHBoxLayout {padding: 0px; margin: 0px;}
            QLabel {padding: 0px; margin: 0px; qproperty-alignment: 'AlignVCenter | AlignLeft';}
            """)
        if action == 'deleted':
            self.setStyleSheet("""
            QHBoxLayout {padding: 0px; margin: 0px;}
            QLabel {padding: 0px; margin: 0px; qproperty-alignment: 'AlignVCenter | AlignLeft';}
            """)

class Block(QWidget):
    def __init__(self, block: BlockData):
        super().__init__()
        self.block = block
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        for line in block.lines:
            layout.addWidget(Line(line, action=block.action))

        self.setLayout(layout)
        if block.action == 'added':
            self.setStyleSheet("""
                QWidget {
                    background-color: #c3e6ac;
                }
            """)

        if block.action == 'deleted':
            self.setStyleSheet("""
            
                QWidget {
                    background-color: #eda39f;
                }
            """)



from dataclasses import dataclass
import difflib


@dataclass
class LineData:
    text: str
    line_num: int


@dataclass
class BlockData:
    lines: list[LineData]
    action: str


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

    print("OVO IMA")
    for line in diff:
        code, content = line[0], line[2:]

        if code == '-':
            if current_block.action != "deleted":
                add_block()
                current_block = BlockData(lines=[], action="deleted")
            current_block.lines.append(LineData(text=content, line_num=line_num1))
            line_num1 += 1

        elif code == '+':
            if current_block.action != "added":
                add_block()
                current_block = BlockData(lines=[], action="added")
            current_block.lines.append(LineData(text=content, line_num=line_num2))
            line_num2 += 1

        elif code == ' ':
            if current_block.action != "none":
                add_block()
                current_block = BlockData(lines=[], action="none")
            current_block.lines.append(
                LineData(text=content, line_num=line_num1))
            line_num1 += 1
            line_num2 += 1

    print("OOOOO")
    add_block()

    return result



def build_diff_lines(original: str, ai: str):
    blocks = analyze_diff(original, ai)

    for block in blocks:
        yield Block(block)
    # return [
    #     Block(block) for block in blocks
    # ]


if __name__ == "__main__":
    print(analyze_diff(
        """1
        2 i
        3
        4
        5
        6
        7
        8""",
        """1
        2 i
        3
        """
    ))