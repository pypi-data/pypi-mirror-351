import logging
import socket
import traceback
from io import BytesIO
from typing import List, TypedDict, Any
from cbor2 import dumps, CBORDecoder

from rewrite_remote.handlers.pypi_manager import Option, PyPiManager
from rewrite_remote.remoting import (
    OK,
    RemotingExecutionContextView,
    RemotingMessageType,
    RemotingMessenger,
)

from rewrite_remote.remote_utils import COMMAND_END
from rewrite_remote.remoting import RemotingContext
from rewrite_remote.handlers.handler_helpers import respond_with_error

from rewrite import InMemoryExecutionContext


logger = logging.getLogger("run_recipe_load_and_visitor_handler")
logger.setLevel(logging.DEBUG)


class RunRecipeLoadAndVisitorArgs(TypedDict):
    recipe_name: str
    recipe_source: str
    recipe_options: Any  # List[recipeOption]


def decode_run_recipe_load_and_visitor_args(
    decoder: CBORDecoder,
) -> RunRecipeLoadAndVisitorArgs:
    """
    Decodes the arguments (order matters and must match the order encoded)
    """
    recipe_name = str(decoder.decode())
    recipe_source = str(decoder.decode())
    recipe_options = decoder.decode()

    return {
        "recipe_name": recipe_name,
        "recipe_source": recipe_source,
        "recipe_options": recipe_options,
    }


def run_recipe_load_and_visitor_handler(
    stream: BytesIO, sock: socket.socket, remoting_ctx: RemotingContext
) -> None:
    remoting_ctx.reset()

    # Read input from stream
    try:
        data = stream.read()
        decoder = CBORDecoder(BytesIO(data))
        args = decode_run_recipe_load_and_visitor_args(decoder)
        recipe_name = args.get("recipe_name")
        recipe_source = args.get("recipe_source")
        recipe_options: List[Option] = args.get("recipe_options") or []
    except Exception as e:  # pylint: disable=broad-except
        respond_with_error(f"Failed to decode arguments: {e}", sock)
        return

    if recipe_name is None:
        respond_with_error("recipe_name is required", sock)
        return

    if recipe_source is None:
        respond_with_error("recipe_source is required", sock)
        return

    # Log the request
    logger.info(f"""Handling run-recipe-load-and-visitor request: {{
        recipe_name: {recipe_name},
        recipe_source: {recipe_source},
        recipe_options: {recipe_options},
    }}""")

    # Receive the tree
    if not hasattr(RemotingMessenger, "_state"):
        RemotingMessenger._state = None

    if not hasattr(RemotingMessenger, "_context"):
        RemotingMessenger._context = remoting_ctx

    received = None
    try:
        received = RemotingMessenger.receive_tree(
            RemotingMessenger, decoder, RemotingMessenger._state
        )
    except Exception as e:
        logging.error(f"Failed to receive tree: {e}")
        logging.error(traceback.format_exc())
        respond_with_error(f"Failed to receive tree: {e}", sock)
        return

    # Set the execution context
    ctx = InMemoryExecutionContext()
    RemotingExecutionContextView.view(ctx).remoting_context = remoting_ctx

    try:
        recipe_instance = PyPiManager.load_recipe(recipe_name, recipe_source, recipe_options)
    except Exception as e:
        respond_with_error(f"Failed to load recipe: {e}", sock)
        return

    # 4. Run the recipe
    try:
        tree_visitor = recipe_instance.get_visitor()

        if not hasattr(tree_visitor, "visit") or not callable(tree_visitor.visit):
            raise ValueError("Visitor does not have a visit method")

        RemotingMessenger._state = tree_visitor.visit(received, ctx)

        if RemotingMessenger._state is None:
            raise ValueError("RemotingMessenger.state cannot be None")
    except Exception as e:
        logging.error(f"Failed to process input data with recipe: {e}")
        logging.error(traceback.format_exc())
        respond_with_error(f"Failed to process input data with recipe: {e}", sock)
        return

    # 5. Write the response
    response_encoder = BytesIO()
    RemotingMessenger.send_tree(
        RemotingMessenger, response_encoder, RemotingMessenger._state, received
    )

    response_data = BytesIO()
    response_data.write(dumps(RemotingMessageType.Response))
    response_data.write(dumps(OK))

    response_data.write(response_encoder.getvalue())

    response_data.write(COMMAND_END)

    sock.sendall(response_data.getvalue())
    logger.info("Request completed.")
