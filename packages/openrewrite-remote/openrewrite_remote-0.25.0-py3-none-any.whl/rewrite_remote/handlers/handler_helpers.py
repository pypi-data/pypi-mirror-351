import logging
import socket
import cbor2

from rewrite_remote.remote_utils import COMMAND_END
from rewrite_remote import RemotingMessageType, ERROR


def respond_with_error(message: str, sock: socket.socket) -> None:
    logging.error(f"[Server] Error: {message}")
    encoded_message = b""
    encoded_message += cbor2.dumps(RemotingMessageType.Response)
    encoded_message += cbor2.dumps(ERROR)
    encoded_message += cbor2.dumps(message)
    encoded_message += COMMAND_END
    sock.sendall(encoded_message)
