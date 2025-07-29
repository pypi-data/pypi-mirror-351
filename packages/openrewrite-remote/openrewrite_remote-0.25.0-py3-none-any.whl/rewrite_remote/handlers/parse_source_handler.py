import logging
import socket
from io import BytesIO, StringIO
from pathlib import Path

import cbor2
from rewrite import (
    ExecutionContext,
    InMemoryExecutionContext,
    ParserInput,
)
from rewrite.python.parser import PythonParserBuilder

from rewrite_remote.remote_utils import COMMAND_END
from rewrite_remote.remoting import (
    OK,
    RemotingContext,
    RemotingMessageType,
)

logger = logging.getLogger("parse_source_handler")
logger.setLevel(logging.DEBUG)


def parse_source_handler(
    stream: BytesIO, sock: socket.socket, remoting_ctx: RemotingContext
) -> None:
    remoting_ctx.reset()

    # Read input from stream
    parser = PythonParserBuilder().build()
    source = cbor2.load(stream)
    ctx = InMemoryExecutionContext()
    ctx.put_message(ExecutionContext.REQUIRE_PRINT_EQUALS_INPUT, False)
    for cu in parser.parse_inputs(
        [ParserInput(Path("source.py"), None, True, lambda: StringIO(source))],
        None,
        ctx,
    ):
        response_stream = BytesIO()
        cbor2.dump(RemotingMessageType.Response, response_stream)
        cbor2.dump(OK, response_stream)
        source_stream = BytesIO()
        remoting_ctx.new_sender_context(source_stream).send_any_tree(cu, None)
        cbor2.dump(source_stream.getvalue(), response_stream)
        cbor2.dump(COMMAND_END, response_stream)
        sock.sendall(response_stream.getvalue())

    logger.info("Request completed.")
