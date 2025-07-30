import os
import http.server
import socketserver
import threading
import time
import importlib.util
from typing import Callable, Dict, Union

from .page import Page

class SyqlorixDevServerHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, routes_map=None, **kwargs):
        self.routes_map = routes_map if routes_map is not None else {}
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self):
        path = self.path.split('?')[0]
        if path.endswith('/'):
            path = path[:-1]
        if path == '':
            path = '/'

        if path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
            return

        if path in self.routes_map:
            page_source = self.routes_map[path]
            try:
                if isinstance(page_source, Page):
                    html_content = page_source.render()
                elif callable(page_source):
                    html_content = page_source().render()
                else:
                    self.send_error(500, "Invalid page source in route map.")
                    return
            except Exception as e:
                self.send_error(500, f"Error rendering page: {e}")
                self.log_error(f"Error rendering page for path {path}: {e}")
                return

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html_content.encode("utf-8"))
        else:
            try:
                super().do_GET() 
            except FileNotFoundError:
                self.send_error(404, "Page not found")

class SyqlorixDevServer(socketserver.TCPServer):
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass, routes_map, bind_and_activate=True):
        self.routes_map = routes_map
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)

    def finish_request(self, request, client_address):
        self.RequestHandlerClass(request, client_address, self, routes_map=self.routes_map)


def serve_pages_dev(routes: Dict[str, Union[Page, Callable[[], Page]]], port: int = 8000):
    original_cwd = os.getcwd()
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_script_dir)) 
    os.chdir(project_root)

    server_instance_holder = {}

    def _start_server():
        Handler = lambda *args, **kwargs: SyqlorixDevServerHandler(
            *args, 
            directory=project_root, 
            routes_map=routes, 
            **kwargs
        )
        with SyqlorixDevServer(("", port), Handler, routes_map=routes) as httpd:
            server_instance_holder['httpd'] = httpd
            print(f"Syqlorix Dev Server running at http://localhost:{port}/")
            print("Available routes:")
            for route_path in routes.keys():
                print(f"  - http://localhost:{port}{route_path}")
            httpd.serve_forever()

    server_thread = threading.Thread(target=_start_server, daemon=True)
    server_thread.start()

    time.sleep(1.0)

    print("\n" + "="*50)
    print(" Your Syqlorix site is ready! ")
    print(" Access it via the Codespaces 'Ports' tab or click a link above.")
    print(f"   Main page: http://localhost:{port}/")
    print("="*50 + "\n")
    print("Press Enter to close the server and exit...")
    input()

    if 'httpd' in server_instance_holder and server_instance_holder['httpd']:
        print("Shutting down Syqlorix Dev Server...")
        server_instance_holder['httpd'].shutdown()
        server_instance_holder['httpd'].server_close()
    
    server_thread.join(timeout=1)

    os.chdir(original_cwd)
    print("Server closed. Goodbye!")