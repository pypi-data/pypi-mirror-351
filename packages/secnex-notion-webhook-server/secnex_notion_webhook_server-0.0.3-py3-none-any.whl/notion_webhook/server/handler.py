from typing import Callable, Tuple, Dict, Any
from src.notion_webhook.db import TokenDatabase
import json

class Handler:
    def __init__(self, handler: Callable[[Dict[str, str], Dict[str, Any], Dict[str, str]], Tuple[int, bytes]]) -> None:
        self.handler = handler

    def __call__(self, headers: Dict[str, str], data: Dict[str, Any], query_params: Dict[str, str]) -> Tuple[int, bytes]:
        return self.handler(headers, data, query_params)

class WebhookHandler:
    def __init__(self, db: TokenDatabase) -> None:
        self.db = db

    def webhook_handler(self, headers: Dict[str, str], data: Dict[str, Any], query_params: Dict[str, str]) -> Tuple[int, bytes]:
        token = query_params.get("token", [None])[0] or headers.get("Authorization", "").split(" ")[1]
        if not token:
            return 401, json.dumps({"status": "error", "message": "Authorization is required"}).encode()
        if not self.db.verify_token(token):
            return 401, json.dumps({"status": "error", "message": "Invalid token"}).encode()
        
        response = {
            "status": "success",
            "message": "Hello, World!",
            "received_data": data
        }
        return 200, json.dumps(response).encode()