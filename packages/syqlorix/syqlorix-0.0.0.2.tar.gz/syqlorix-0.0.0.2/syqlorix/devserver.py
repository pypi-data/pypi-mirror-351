import os
import http.server
import socketserver
import threading
import time


from .page import Page 


class SyqlorixDevServerHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, html_content=None, **kwargs):
        self.html_content = html_content
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self.html_content.encode("utf-8"))
        else:
            super().do_GET()

class SyqlorixDevServer(socketserver.TCPServer):
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass, html_content, bind_and_activate=True):
        self.html_content = html_content
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)

    def finish_request(self, request, client_address):
        self.RequestHandlerClass(request, client_address, self, html_content=self.html_content)


def serve_page_dev(page_obj: Page, port: int = 8000):
    html_output = page_obj.render()
    
    original_cwd = os.getcwd()
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_script_dir)) 
    os.chdir(project_root)

    server_instance_holder = {}

    def _start_server():
        Handler = lambda *args, **kwargs: SyqlorixDevServerHandler(
            *args, 
            directory=project_root, 
            html_content=html_output, 
            **kwargs
        )
        with SyqlorixDevServer(("", port), Handler, html_content=html_output) as httpd:
            server_instance_holder['httpd'] = httpd
            print(f"Syqlorix Dev Server running at http://localhost:{port}/")
            httpd.serve_forever()

    server_thread = threading.Thread(target=_start_server, daemon=True)
    server_thread.start()

    time.sleep(1.0)

    print("\n" + "="*50)
    print(" Your Syqlorix page is ready! ")
    print(" Access it via the Codespaces 'Ports' tab or click this link:")
    print(f"   http://localhost:{port}/")
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