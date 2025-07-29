# Copyright (C) 2021-2025 Aleksandr Popov

# This program is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Lesser GNU General Public License for more details.

# You should have received a copy of the Lesser GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""The tool for visual testing of widgets."""

import sys
from qtpy import QtWidgets
from qtpy.QtCore import Qt

__version__ = "0.1.3"


class TestApp:
    """An application for displaying a widget that has been set to a
    certain state and asking questions that express the requirements
    of the test case.

    Parameters
    ----------
    context: unittest.TestCase
        The class in that the test case should being ran.
    """

    # pylint: disable=too-few-public-methods

    __app = None

    def __init__(self, context):
        if not TestApp.__app:
            TestApp.__app = QtWidgets.QApplication(sys.argv)

        self.answer = False
        self.dialog = _Dialog(self)
        self.context = context

    def __call__(self, widget, assertions):
        self.dialog.set_widget(widget)
        self.dialog.set_assertions(assertions)

        self.dialog.show()
        TestApp.__app.exec()

        self.context.assertTrue(self.answer)


class _Dialog(QtWidgets.QDialog):

    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.__make_gui()

    def set_widget(self, widget):
        """Set widget to be shown."""
        self.l_widget.addWidget(widget)

    def set_assertions(self, assertions):
        """Set assertions to be printed in dialog."""
        lines = ""
        for asr in assertions:
            lines += f"- {asr}\n"

        self.label_assert.setText(lines)

    def __on_button_no(self):
        self.app.answer = False
        self.reject()

    def __on_button_yes(self):
        self.app.answer = True
        self.accept()

    def __make_gui(self):
        layout = QtWidgets.QVBoxLayout(self)

        self.l_widget = QtWidgets.QHBoxLayout()
        layout.addLayout(self.l_widget)

        self.l_assert = QtWidgets.QHBoxLayout()
        layout.addLayout(self.l_assert)

        self.label_assert = QtWidgets.QLabel("")
        self.label_assert.setWordWrap(True)
        self.l_assert.addWidget(self.label_assert)

        self.l_button = QtWidgets.QHBoxLayout()
        layout.addLayout(self.l_button)

        self.b_no = QtWidgets.QPushButton("No")
        self.b_no.clicked.connect(self.__on_button_no)
        self.l_button.addWidget(self.b_no)

        self.b_yes = QtWidgets.QPushButton("Yes")
        self.b_yes.clicked.connect(self.__on_button_yes)
        self.l_button.addWidget(self.b_yes)

        self.b_yes.setFocus(Qt.ActiveWindowFocusReason)
