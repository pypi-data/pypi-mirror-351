import logging
import socket
from io import BytesIO
from typing import List, TypedDict
from cbor2 import dumps, CBORDecoder

from rewrite_remote.remote_utils import COMMAND_END
from rewrite_remote.remoting import OK, RemotingContext, RemotingMessageType
from rewrite_remote.handlers.handler_helpers import respond_with_error
from rewrite_remote.handlers.pypi_manager import PyPiManager, Source
from rewrite_remote.handlers.types import PackageSource

logger = logging.getLogger("recipe_install_handler")
logger.setLevel(logging.DEBUG)


class RecipeInstallArgs(TypedDict):
    package_id: str
    package_version: str
    include_default_repository: bool
    package_sources: List[PackageSource]


def decode_recipe_install_args(decoder: CBORDecoder) -> RecipeInstallArgs:
    """
    Decodes the arguments (order matters and must match the order encoded)
    """
    package_id = str(decoder.decode())
    package_version = str(decoder.decode())
    include_default_repository = bool(decoder.decode())
    package_sources_data = decoder.decode()

    if not isinstance(package_sources_data, list):
        raise ValueError("package_sources_data is not a list")

    package_sources = []
    if package_sources_data and len(package_sources_data) > 0:
        package_sources = [
            PackageSource(source=ps.get("source"), credential=ps.get("credential"))
            for ps in package_sources_data
        ]

    return {
        "package_id": package_id,
        "package_version": package_version,
        "include_default_repository": include_default_repository,
        "package_sources": package_sources,
    }


# Main command handler with the specified signature
def recipe_install_handler(
    stream: BytesIO, sock: socket.socket, remoting_ctx: RemotingContext
) -> None:
    remoting_ctx.reset()

    # 1. Read input from stream
    try:
        data = stream.read()
        decoder = CBORDecoder(BytesIO(data))
        args = decode_recipe_install_args(decoder)
        package_id = args.get("package_id")
        package_version = args.get("package_version")
        include_default_repository = args.get("include_default_repository")
        package_sources = args.get("package_sources")
    except Exception as e:  # pylint: disable=broad-except
        respond_with_error(f"Failed to decode arguments: {e}", sock)
        return

    if package_id is None:
        respond_with_error("package_id is required", sock)
        return

    if package_version is None:
        respond_with_error("package_version is required", sock)
        return

    if package_sources is None:
        respond_with_error("package_sources is required", sock)
        return

    if include_default_repository is None:
        respond_with_error("include_default_repository is required", sock)
        return

    # 2. Log the request
    logger.info(f"""Handling install-recipe request: {{
        packageId: {package_id},
        packageVersion: {package_version},
        packageSources: {package_sources},
        includeDefaultRepository: {include_default_repository},
    }}""")

    # 3. Validate sources
    sources: List[Source] = [
        Source(
            source=ps.source,
            username=ps.credential.get("username") if ps.credential else None,
            password=ps.credential.get("password") if ps.credential else None,
            token=ps.credential.get("token") if ps.credential else None,
        )
        for ps in package_sources or []
    ]

    valid_source = PyPiManager.find_valid_source(
        package_id, package_version, sources, include_default_repository
    )

    if not valid_source:
        respond_with_error("No valid sources found", sock)
        return

    # 4. Install the recipe
    try:
        installable_recipes = PyPiManager.install_package(package_id, package_version, valid_source)
    except Exception as e:  # pylint: disable=broad-except
        respond_with_error(f"Failed to install package: {e}", sock)
        return

    # 5. Log the result
    logger.info(
        "Found %d recipe(s) for package %s",
        len(installable_recipes.recipes),
        package_id,
    )
    for recipe in installable_recipes.recipes:
        logger.info("  Resolved recipe %s from %s", recipe, valid_source.source)

    # 6. Write response to stream
    response = {
        "recipes": [
            {
                "name": recipe.name,
                "source": recipe.source,
                "options": [],
            }
            for recipe in installable_recipes.recipes
        ],
        "repository": installable_recipes.source,
        "version": installable_recipes.version,
    }

    # Encode the response using CBOR
    response_data = BytesIO()
    response_data.write(dumps(RemotingMessageType.Response))
    response_data.write(dumps(OK))
    response_data.write(dumps(response))
    response_data.write(COMMAND_END)

    sock.sendall(response_data.getvalue())

    logger.info("Request completed.")
