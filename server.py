import http.server
import socketserver
import os
import mimetypes
import sys

# Ensure correct MIME types for frontend files
mimetypes.add_type('application/javascript', '.ts')
mimetypes.add_type('application/javascript', '.tsx')
mimetypes.add_type('application/javascript', '.jsx')
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('image/svg+xml', '.svg')
mimetypes.add_type('application/json', '.json')
mimetypes.add_type('application/xml', '.xml')

class RobustHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers for local development if needed
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def do_GET(self):
        # 1. Clean path (remove query params)
        path = self.path.split('?')[0]

        # 2. Suppress 404 logs for optional map files or missing favicons if they don't exist
        if path.endswith('.map') or path == '/favicon.ico':
            if not os.path.exists(self.translate_path(path)):
                self.send_response(204) # No Content
                self.end_headers()
                return

        # 3. Handle explicit file requests
        if os.path.exists(self.translate_path(path)) and os.path.isfile(self.translate_path(path)):
            super().do_GET()
            return

        # 4. Handle missing extensions (React imports usually omit .tsx/.ts)
        base_path = self.translate_path(path)
        # Extensions to check in order of preference
        extensions = ['.tsx', '.ts', '.jsx', '.js', '.css']

        for ext in extensions:
            if os.path.exists(base_path + ext):
                self.path = path + ext
                super().do_GET()
                return

        # 5. Redirect unknown paths or routes to home
        filename = os.path.basename(path)
        if path != '/' and ('.' not in filename or not os.path.exists(self.translate_path(path))):
             self.send_response(302)
             self.send_header('Location', '/')
             self.end_headers()
             return

        # 6. Default behavior (will 404)
        super().do_GET()

def start_server():
    print("------------------------------------------------")
    print("   SMSKenya Local Server")
    print("------------------------------------------------")

    default_port = 8000
    if len(sys.argv) > 1:
        try:
            default_port = int(sys.argv[1])
        except ValueError:
            pass

    try:
        port_input = input(f"Enter the port you want to use (default {default_port}): ")
        port = int(port_input) if port_input.strip() else default_port
    except ValueError:
        print(f"Invalid input. Using default port {default_port}.")
        port = default_port

    try:
        # Allow reuse of address
        socketserver.TCPServer.allow_reuse_address = True

        print(f"\nServer started successfully!")
        print(f"Serving at: http://localhost:{port}")
        print("Press Ctrl+C to stop the server.")

        with socketserver.TCPServer(("", port), RobustHandler) as httpd:
            httpd.serve_forever()
    except OSError as e:
        print(f"\nError starting server: {e}")
        print("Try using a different port number.")
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    if os.path.exists('dist'):
        os.chdir('dist')
        print("Serving 'dist' directory...")
    else:
        print("Warning: 'dist' directory not found. Serving current directory.")

    start_server()