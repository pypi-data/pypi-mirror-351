from io import BytesIO
import traceback
import socket

import cbor2

from rewrite_remote import RemotingContext, RemotingMessageType, OK, ERROR


def hello_world_handler(
    stream: BytesIO, sock: socket.socket, remoting_ctx: RemotingContext
) -> None:
    """
    A simple handler that responds to hello world command and response with string world
    """
    try:
        remoting_ctx.reset()
        request = cbor2.load(stream)

        if request != "hello":
            print("Did not receive 'hello' ")
            raise ValueError(f"Unexpected request: {request}")

        # Prepare a response
        response_stream = BytesIO()
        cbor2.dump(RemotingMessageType.Response, response_stream)
        cbor2.dump(OK, response_stream)
        cbor2.dump("world", response_stream)
        sock.sendall(response_stream.getvalue())

    except (socket.error, cbor2.CBORDecodeError) as e:
        print(f"Error in hello handler: {e}")
        traceback.print_exc()
        # Send an error response if something goes wrong
        response_stream = BytesIO()
        cbor2.dump(RemotingMessageType.Response, response_stream)
        cbor2.dump(ERROR, response_stream)
        cbor2.dump(traceback.format_exc(), response_stream)
        sock.sendall(response_stream.getvalue())
