import argparse
from os import getcwd

from .client.fsclient import FSClient
from .server import Server


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="fbdc",
        description="Filesystem Based Discord Client"
    )
    parser.add_argument(
        "token",
        help="Your token"
    )
    parser.add_argument(
        "-r", "--root",
        default=getcwd(),
        metavar="PATH",
        help="Root of the bot"
    )
    args = parser.parse_args()
    
    client = FSClient(args.root)
    server = Server(args.token, client)

    server.start()
