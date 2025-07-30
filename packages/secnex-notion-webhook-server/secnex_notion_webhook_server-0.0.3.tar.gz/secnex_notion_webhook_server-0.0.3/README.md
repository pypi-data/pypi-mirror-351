# Notion Webhook Server

This is a simple python package to create a webhook server that can be used to handle Notion webhooks and trigger actions.

## Installation

```bash
pip install secnex-notion-webhook-server
```

## Usage

### Create a new webhook server with only the webhook handler

```python
from notion_webhook.server import WebhookServer

server = WebhookServer()
server.start()
```

### Create a new webhook server with a custom handler

```python
from notion_webhook.server import Server, Handler, WebhookHandler
from notion_webhook.db import TokenDatabase

db = TokenDatabase()

if db.check_first_run():
    token_id, token = db.create_token()
    print(token)

handler = Handler(WebhookHandler(db).webhook_handler)

handlers = {
    "/webhook": handler
}

server = Server(
    addr=os.getenv("HOST", "0.0.0.0"),
    port=int(os.getenv("PORT", 8000)),
    handlers=handlers,
    app_name=os.getenv("APP_NAME", "NotionWebhookServer")
)
server.start()
```

_You find the example in the [examples](examples) folder._

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Contact

For questions or support, please contact us at [support@secnex.io](mailto:support@secnex.io).
