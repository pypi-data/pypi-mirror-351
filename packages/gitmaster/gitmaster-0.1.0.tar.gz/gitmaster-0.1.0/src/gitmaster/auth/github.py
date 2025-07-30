import webbrowser
import requests
import http.server
import socketserver
import threading
import os
import keyring
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8765/callback"
TOKEN_SERVICE = "gitmaster"
TOKEN_USERNAME = "github_token"

def save_token(token):
    keyring.set_password(TOKEN_SERVICE, TOKEN_USERNAME, token)

def get_token():
    return keyring.get_password(TOKEN_SERVICE, TOKEN_USERNAME)

def delete_token():
    keyring.delete_password(TOKEN_SERVICE, TOKEN_USERNAME)

class OAuthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/callback?code="):
            code = self.path.split("code=")[1]
            token = exchange_code_for_token(code)
            if token:
                save_token(token)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"<h1>Login successful. You can close this window.</h1>")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"<h1>Login failed.</h1>")
        else:
            self.send_error(404)

def start_server():
    with socketserver.TCPServer(("localhost", 8765), OAuthHandler) as httpd:
        httpd.handle_request()

def exchange_code_for_token(code):
    url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    response = requests.post(url, headers=headers, data=data)
    if response.ok:
        return response.json().get("access_token")
    return None

def login():
    auth_url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=repo"
    webbrowser.open(auth_url)
    server_thread = threading.Thread(target=start_server)
    server_thread.start()
    server_thread.join()

def logout():
    delete_token()
