#!/usr/bin/env python3
"""
Desktop launcher for the Scientific Calculator.

Uses pywebview to wrap the web frontend in a native desktop window.
The FastAPI backend runs in a background thread.
"""

import sys
import time
import threading
import signal
import atexit
import traceback
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

# Ensure the project root is importable when this script is run directly
# (e.g. `python desktop/run.py`), so `backend` can be imported.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    import webview
except ImportError:
    print("Error: pywebview is not installed. Run: pip install pywebview")
    sys.exit(1)


def find_free_port():
    """Find a free port for the backend server."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


class CalculatorApp:
    def __init__(self):
        self.port = find_free_port()
        self.backend_thread = None
        self.backend_error = None  # populated if the backend thread crashes
        self.window = None

    def run_backend(self):
        """Run the FastAPI backend server (runs in a background thread)."""
        import uvicorn
        try:
            from backend.main import app
        except Exception:
            self.backend_error = traceback.format_exc()
            return
        try:
            uvicorn.run(app, host='127.0.0.1', port=self.port, log_level="warning")
        except Exception:
            self.backend_error = traceback.format_exc()

    def start_backend(self):
        """Start the FastAPI backend in a background thread and wait for it."""
        print(f"Starting backend on port {self.port}...")
        self.backend_thread = threading.Thread(target=self.run_backend, daemon=True)
        self.backend_thread.start()

        health_url = f'http://127.0.0.1:{self.port}/health'
        # Poll up to ~10 seconds for the server to come up.
        for _ in range(100):
            # Surface a backend crash immediately instead of looping silently.
            if self.backend_error is not None:
                print("Backend thread crashed:\n" + self.backend_error)
                return False
            time.sleep(0.1)
            try:
                with urlopen(health_url, timeout=1) as resp:
                    if resp.status == 200:
                        print("Backend is ready!")
                        return True
            except URLError:
                continue
            except Exception:
                continue

        print("Error: Backend did not become ready in time.")
        if self.backend_error is not None:
            print("Backend thread error:\n" + self.backend_error)
        return False

    def create_window(self):
        """Create the pywebview window pointing to the served frontend."""
        # The backend serves the frontend over HTTP at "/", so we load that
        # URL directly. The frontend then uses window.location.origin for API
        # calls (same origin, no CORS / file:// problems).
        url = f"http://127.0.0.1:{self.port}/"

        self.window = webview.create_window(
            title='Scientific Calculator',
            url=url,
            width=480,
            height=700,
            resizable=True,
            min_size=(400, 600),
            frameless=False,
            easy_drag=True,
            on_top=False,
        )
        return self.window

    def run(self):
        """Run the desktop application."""
        print("Starting Scientific Calculator...")
        if not self.start_backend():
            sys.exit(1)

        self.create_window()
        if not self.window:
            sys.exit(1)

        print("Launching window...")
        webview.start(debug=False)

    def cleanup(self):
        print("Shutting down...")


def main():
    app = CalculatorApp()

    def signal_handler(sig, frame):
        app.cleanup()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(app.cleanup)

    try:
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        app.cleanup()
        sys.exit(1)


if __name__ == '__main__':
    main()
