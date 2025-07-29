import logging
import socket
from io import BytesIO
from typing import List
from cbor2 import dumps, CBORDecoder

from rewrite_remote.handlers.project_helper import list_sub_projects
from rewrite_remote.remote_utils import COMMAND_END
from rewrite_remote.remoting import OK, RemotingContext, RemotingMessageType
from rewrite_remote.handlers.handler_helpers import respond_with_error

logger = logging.getLogger("list_projects_handler")
logger.setLevel(logging.DEBUG)


# Main command handler with the specified signature
def list_projects_handler(
    stream: BytesIO, sock: socket.socket, remoting_ctx: RemotingContext
) -> None:
    remoting_ctx.reset()

    # 1. Read input from stream
    try:
        data = stream.read()
        decoder = CBORDecoder(BytesIO(data))
        root_project_file = str(decoder.decode())
    except Exception as e:  # pylint: disable=broad-except
        respond_with_error(f"Failed to decode arguments: {e}", sock)
        return

    if root_project_file == "" or root_project_file is None:
        respond_with_error("root_project_file is required", sock)
        return

    # 2. Log the request
    logger.info(f"""Handling list-recipe request: {{
        root_project_file: {root_project_file},
    }}""")

    # 3. Find projects
    projects = list_sub_projects(root_project_file)

    project_config_files: List[str] = [root_project_file]

    for project in projects:
        project_config_files.append(project.project_root + "/pyproject.toml")

    # 4. Log the result
    logger.info("Found %d project(s)", len(project_config_files))
    for project in project_config_files:
        logger.info(
            "Found project: %s",
            project,
        )

    # 5. Write response to stream
    response_data = BytesIO()
    response_data.write(dumps(RemotingMessageType.Response))
    response_data.write(dumps(OK))
    response_data.write(dumps(project_config_files))
    response_data.write(COMMAND_END)
    sock.sendall(response_data.getvalue())

    logger.info("Request completed.")
