"""Entry point: python -m picrawler_server or picrawler-server CLI."""

import logging
import os

import uvicorn


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    port = int(os.environ.get("PICRAWLER_PORT", "8000"))
    uvicorn.run("picrawler_server.app:create_app", host="0.0.0.0", port=port, factory=True)


if __name__ == "__main__":
    main()
