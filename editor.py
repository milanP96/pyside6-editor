from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QTextEdit


class MyEditor(QTextEdit):
    def __init__(self, parent=None):
        super(MyEditor, self).__init__(parent)
        self.setStyleSheet("""
        background: #F0EDCC;
        color: #02343F;
        border: 1px solid black; 
        border-radius: 10px;
        padding: 10px;
        """
        )

    def acceptRichText(self):
        return False

    def focus_on_line(self, line_number):
        # Get the cursor and move it to the specified line
        cursor = self.textCursor()

        # Move to the beginning of the specified line
        cursor.movePosition(QTextCursor.Start)
        for _ in range(line_number):
            cursor.movePosition(QTextCursor.Down)

        # Set the cursor to the QTextEdit
        self.setTextCursor(cursor)

        self.ensureCursorVisible()
        # Set focus on the QTextEdit
        self.setFocus()