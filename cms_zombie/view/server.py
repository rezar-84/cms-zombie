import http.server
import json
import socketserver
import webbrowser
from pathlib import Path
from .collector import StateCollector

class ViewServer:
    """Renders and optionally serves the migration reporting dashboard."""

    @classmethod
    def render_html(cls, project_dir: Path) -> str:
        project_dir = Path(project_dir)
        state = StateCollector.collect(project_dir)
        state_json = json.dumps(state)

        tpl_path = Path(__file__).parent / "template.html"
        html = tpl_path.read_text(encoding="utf-8")
        html = html.replace("__PROJECT_NAME__", project_dir.name)
        html = html.replace("__STATE_JSON__", state_json)
        return html

    @classmethod
    def write_static_report(cls, project_dir: Path, output_file: Path = None) -> Path:
        html = cls.render_html(project_dir)
        if output_file is None:
            output_file = Path(project_dir) / "migration-report.html"
        output_file = Path(output_file)
        output_file.write_text(html, encoding="utf-8")
        return output_file

    @classmethod
    def serve(cls, project_dir: Path, port: int = 8765, open_browser: bool = True):
        project_dir = Path(project_dir)

        class Handler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path in ("/", "/index.html"):
                    html = ViewServer.render_html(project_dir)
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(html.encode("utf-8"))
                elif self.path == "/api/state":
                    state = StateCollector.collect(project_dir)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(state).encode("utf-8"))
                else:
                    self.send_error(404, "Not Found")

            def log_message(self, format, *args):
                return # quiet server logs

        with socketserver.TCPServer(("", port), Handler) as httpd:
            url = f"http://localhost:{port}"
            print(f"[+] CMS Zombie View live at: {url}")
            print("    Press Ctrl+C to stop.")
            if open_browser:
                webbrowser.open(url)
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n[*] Stopping view server.")
