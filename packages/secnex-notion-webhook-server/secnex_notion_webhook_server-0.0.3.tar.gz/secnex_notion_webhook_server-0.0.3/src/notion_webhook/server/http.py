from http.server import HTTPServer, BaseHTTPRequestHandler
from .handler import Handler, WebhookHandler
from src.notion_webhook.db import TokenDatabase

import os
import json
import logging

from typing import Optional, Callable
from urllib.parse import urlparse, parse_qs

class Server:
    def __init__(
        self, 
        addr: str = "0.0.0.0", 
        port: int = 8000, 
        handlers: dict[str, Handler] = None,
        log_level: int = logging.INFO,
        log_format: str = "%(asctime)s [%(levelname)s] - %(name)s: %(message)s",
        log_handler: Optional[Callable] = None,
        log_requests: bool = True,
        app_name: str = "NotionWebhookServer"
    ) -> None:
        self.addr = addr
        self.port = port
        self.handlers = handlers or {}
        self.log_requests = log_requests
        
        # Logging Setup
        self.logger = logging.getLogger(app_name)
        self.logger.setLevel(log_level)
        
        if log_handler:
            self.logger.addHandler(log_handler)
        else:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                fmt=log_format,
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        self.httpd = HTTPServer((self.addr, self.port), self._make_handler())

    def start(self):
        self.logger.info(f"Server running on http://{self.addr}:{self.port}")
        self.httpd.serve_forever()

    def _make_handler(self):
        handlers = self.handlers
        logger = self.logger
        log_requests = self.log_requests

        class CustomHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                if log_requests:
                    # Remove query parameters from the path in the log message
                    message = format % args
                    if "?" in message:
                        message = message.split("?")[0] + " HTTP/1.1"
                    logger.info("%s - %s", self.address_string(), message)

            def do_POST(self):
                # Parse URL and get path without query parameters
                parsed_url = urlparse(self.path)
                path = parsed_url.path
                query_params = parse_qs(parsed_url.query)

                if path in handlers:
                    try:
                        content_length = int(self.headers['Content-Length'])
                        post_data = self.rfile.read(content_length)
                        data = json.loads(post_data.decode('utf-8'))
                        logger.debug(f"Received request on {path}: {data}")
                        
                        status_code, response = handlers[path](self.headers, data, query_params)
                        
                        self.send_response(status_code)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(response)
                        logger.debug(f"Sent response: {response.decode()}")
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON data received on {path}")
                        self.send_error(400, "Invalid JSON data")
                else:
                    logger.warning(f"Invalid path requested: {path}")
                    self.send_error(404)

        return CustomHandler
    

class WebhookServer:
    def __init__(self) -> None:
        self.db = TokenDatabase(os.getenv("DB_PATH", "tokens.db"))
        if self.db.check_first_run():
            token_id, token = self.db.create_token()
            print(token)

        self.handlers = {
            "/webhook": Handler(WebhookHandler(self.db).webhook_handler)
        }

        self.server = Server(
            addr=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", 8000)),
            handlers=self.handlers, 
            app_name=os.getenv("APP_NAME", "NotionWebhookServer")
        )

    def start(self):
        self.server.start()