"""PySide6 desktop chat client for Personal AI.

This UI is intentionally isolated from backend internals except for the
`handle_input` function exposed by the assistant core.
"""

from __future__ import annotations

import sys
import traceback
from dataclasses import dataclass
from typing import Any, Dict

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from personal_ai.core.assistant import MODE, handle_input, model


@dataclass
class WorkerResult:
    """Container for worker execution result."""

    payload: Dict[str, Any] | None = None
    error: str | None = None


class WorkerSignals(QObject):
    """Signals emitted by background worker tasks."""

    completed = Signal(object)


class AskWorker(QRunnable):
    """Background worker to avoid blocking the UI thread."""

    def __init__(self, text: str) -> None:
        super().__init__()
        self._text = text
        self.signals = WorkerSignals()

    def run(self) -> None:
        try:
            response = handle_input(self._text)
            self.signals.completed.emit(WorkerResult(payload=response))
        except Exception:  # noqa: BLE001
            self.signals.completed.emit(WorkerResult(error=traceback.format_exc()))


class MainWindow(QMainWindow):
    """Main desktop chat window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Personal AI Desktop")
        self.resize(900, 600)

        self._thread_pool = QThreadPool.globalInstance()

        root = QWidget(self)
        layout = QVBoxLayout(root)

        self.chat_output = QTextEdit(self)
        self.chat_output.setReadOnly(True)
        self.chat_output.setPlaceholderText("Assistant conversation will appear here...")
        self.chat_output.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.output_scroll = QScrollArea(self)
        self.output_scroll.setWidgetResizable(True)
        self.output_scroll.setWidget(self.chat_output)
        layout.addWidget(self.output_scroll)

        input_row = QHBoxLayout()
        self.chat_input = QLineEdit(self)
        self.chat_input.setPlaceholderText("Type your message and press Enter...")
        self.chat_input.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.send_message)

        self.mic_button = QPushButton("Mic (Soon)", self)
        self.mic_button.setEnabled(False)
        self.mic_button.setToolTip("Microphone support will be added in a future iteration.")

        input_row.addWidget(self.chat_input)
        input_row.addWidget(self.send_button)
        input_row.addWidget(self.mic_button)
        layout.addLayout(input_row)

        self.setCentralWidget(root)

        status = QStatusBar(self)
        status.showMessage(f"Mode: {MODE.upper()} | Model loaded: {'Yes' if model is not None else 'No'}")
        self.setStatusBar(status)

    def append_message(self, role: str, message: str) -> None:
        """Append a chat message in a simple chat-like transcript."""
        safe = message.replace("\n", "<br>")
        self.chat_output.append(f"<b>{role}:</b> {safe}")
        self.chat_output.verticalScrollBar().setValue(self.chat_output.verticalScrollBar().maximum())

    def send_message(self) -> None:
        """Read input and dispatch worker task."""
        text = self.chat_input.text().strip()
        if not text:
            return

        self.chat_input.clear()
        self.append_message("You", text)

        self.send_button.setEnabled(False)
        self.chat_input.setEnabled(False)

        worker = AskWorker(text)
        worker.signals.completed.connect(self._on_worker_completed)
        self._thread_pool.start(worker)

    def _on_worker_completed(self, result: WorkerResult) -> None:
        """Handle background response and update transcript safely."""
        self.send_button.setEnabled(True)
        self.chat_input.setEnabled(True)
        self.chat_input.setFocus(Qt.OtherFocusReason)

        if result.error:
            self.append_message("Assistant", "Sorry, something went wrong while processing your message.")
            QMessageBox.warning(self, "Processing error", "The assistant failed to process your request.")
            print(result.error)
            return

        payload = result.payload or {}
        reply = payload.get("reply", "Done.")
        self.append_message("Assistant", str(reply))

        commands = payload.get("commands", [])
        if commands:
            latest = commands[-1]
            confidence = latest.get("confidence")
            if confidence is not None:
                self.append_message("System", f"Confidence: {float(confidence):.2f}")

            actions = latest.get("actions") or []
            if actions:
                self.append_message("System", f"Actions: {', '.join(actions)}")


def main() -> int:
    """Run the desktop application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
