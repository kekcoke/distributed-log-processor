from http.server import SimpleHTTPRequestHandler
from config import LOG_FILE, LOG_LEVEL_CONSOLE, LOG_LEVEL_FILE, LOG_DIR

class LogHandler(SimpleHTTPRequestHandler):
    """Web interface for viewing logs and configuration."""

    def do_GET(self):
        if self.path == "/" or self.path == "/logs":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            html = self.generate_html()
            self.wfile.write(html.encode())
        elif self.path == "/api/logs":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            logs = self.get_recent_logs()
            self.wfile.write(logs.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def get_recent_logs(self, lines=50):
        """Get recent log entries from the log file."""
        try:
            if LOG_FILE.exists():
                with open(LOG_FILE, "r") as f:
                    all_lines = f.readlines()
                    return "".join(all_lines[-lines:])
        except Exception as e:
            return f"Error reading logs: {e}"
        return "No logs available"

    def generate_html(self):
        """Generate the web interface HTML."""
        config_info = f"""
        <h2>Current Configuration</h2>
        <table>
            <tr><td><strong>Log Directory:</strong></td><td>{LOG_DIR}</td></tr>
            <tr><td><strong>Log File:</strong></td><td>{LOG_FILE}</td></tr>
            <tr><td><strong>Console Log Level:</strong></td><td>{LOG_LEVEL_CONSOLE}</td></tr>
            <tr><td><strong>File Log Level:</strong></td><td>{LOG_LEVEL_FILE}</td></tr>
            <tr><td><strong>Max File Size:</strong></td><td>1MB</td></tr>
            <tr><td><strong>Backup Count:</strong></td><td>5</td></tr>
        </table>
        """
        recent_logs = self.get_recent_logs(100).replace("\n", "<br>")

        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Distributed Logger Service</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        h1 {{ color: #333; }}
        h2 {{ color: #555; margin-top: 30px; }}
        table {{ background: white; padding: 15px; border-radius: 8px; margin: 15px 0; }}
        td {{ padding: 5px 15px 5px 0; }}
        .logs {{ background: #1e1e1e; color: #0f0; padding: 20px; border-radius: 8px;
                 max-height: 400px; overflow-y: auto; font-family: monospace; margin: 15px 0; }}
        .nav {{ margin-bottom: 20px; }}
    </style>
</head>
<body>
    <h1>📋 Distributed Logger Service</h1>
    <div class="nav">
        <a href="/logs">Home</a> |
        <a href="/api/logs">Raw Logs</a>
    </div>

    {config_info}

    <h2>Recent Logs (last 100 lines)</h2>
    <div class="logs">{recent_logs}</div>
</body>
</html>"""

