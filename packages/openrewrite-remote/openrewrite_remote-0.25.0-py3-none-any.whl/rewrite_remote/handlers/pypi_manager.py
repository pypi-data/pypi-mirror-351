import os
import sys
import subprocess
import importlib
import inspect
import pkgutil
import site

from dataclasses import dataclass

from pypi_simple import PyPISimple
from packaging.version import parse as parse_version
from packaging.specifiers import SpecifierSet
from rewrite import Recipe

from typing import Optional, Dict, List, Any

DEFAULT_PYPI_URL = "https://pypi.org/simple"
DEFAULT_RECIPE_INSTALL_LOCATION = os.path.join(".", ".local_python_recipes")

# Ensure that the directory is on sys.path
if DEFAULT_RECIPE_INSTALL_LOCATION not in sys.path:
    sys.path.insert(0, DEFAULT_RECIPE_INSTALL_LOCATION)


class Source:
    def __init__(
        self,
        source: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
    ):
        self.source = source
        self.username = username
        self.password = password
        self.token = token


@dataclass
class Option:
    name: str
    type: str
    required: bool


@dataclass
class InstalledRecipe:
    name: str
    source: str
    options: List[Option]


class InstalledPackage:
    def __init__(
        self,
        name: str,
        version: str,
        source: str,
        recipes: List[InstalledRecipe],
    ):
        self.name = name
        self.version = version
        self.source = source
        self.recipes = recipes


class PyPiManager:
    @staticmethod
    def find_valid_source(
        package_name: str,
        requestedVersion: str,
        package_sources: List[Source],
        include_default_source: bool = True,
    ) -> Optional[Source]:
        """
        Finds a valid source for the specified package using `pip show` with `--index-url`.
        """
        package_identifier = (
            f"{package_name}=={requestedVersion}" if requestedVersion else package_name
        )
        if include_default_source and not any(
            source.source == DEFAULT_PYPI_URL for source in package_sources
        ):
            package_sources.append(Source(source=DEFAULT_PYPI_URL))

        for source in package_sources:
            try:
                authenticated_url = PyPiManager._get_authenticated_url(source)
                result = PyPiManager._package_exists_in_registry(
                    authenticated_url,
                    package_name,
                    requestedVersion,
                )
                if result:
                    print(f"Package {package_identifier} found in source: {source.source}")
                    return source
                else:
                    print(f"Package {package_identifier} not found in source: {source.source}")
            except Exception as e:
                print(f"Error checking source {source.source}: {e}")

        return None

    @staticmethod
    def install_package(
        package_name: str,
        requestedVersion: Optional[str] = None,
        package_source: Optional[Source] = None,
    ) -> InstalledPackage:
        """
        Installs the specified package from a given source.
        """
        package_identifier = (
            f"{package_name}=={requestedVersion}" if requestedVersion else package_name
        )

        pip_command = [
            sys.executable,
            "-m",
            "pip",
            "install",
            package_identifier,
            "--target",
            DEFAULT_RECIPE_INSTALL_LOCATION,
        ]

        if package_source:
            authenticated_url = PyPiManager._get_authenticated_url(package_source)
            pip_command.extend(["--index-url", authenticated_url])
        else:
            pip_command.extend(["--index-url", DEFAULT_PYPI_URL])

        # create directory if it does not exist
        if not os.path.exists(DEFAULT_RECIPE_INSTALL_LOCATION):
            os.makedirs(DEFAULT_RECIPE_INSTALL_LOCATION)

        try:
            subprocess.run(pip_command, check=True)
            metadata = PyPiManager._get_package_metadata(package_name)
            resolvedVersion = metadata.get("version", "")

            discovered_recipes = PyPiManager._introspect_module(package_name)

            return InstalledPackage(
                name=package_name,
                version=resolvedVersion,
                source=package_source.source if package_source else DEFAULT_PYPI_URL,
                recipes=discovered_recipes,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to install package {package_name}: {e}")

    @staticmethod
    def uninstall_package(package_name: str) -> None:
        """
        Uninstalls the specified package using pip.
        """
        try:
            subprocess.run(["pip", "uninstall", "-y", package_name], check=True)
            print(f"Package {package_name} uninstalled successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to uninstall package {package_name}: {e}")

    @staticmethod
    def load_recipe(recipe_name: str, module_name: str, recipe_options: List[Option]) -> Recipe:
        """
        Loads a recipe from the specified source.
        """
        try:
            module = importlib.import_module(module_name)
            recipe = getattr(module, recipe_name)

            has_params = bool(inspect.signature(recipe).parameters)

            if not has_params:
                return recipe()
            else:
                return recipe(recipe_options)
        except Exception as e:
            raise RuntimeError(f"Failed to load recipe {recipe_name}: {e}")

    @staticmethod
    def load_package_details(package_name: str) -> Dict[str, Any]:
        """
        Loads package details using `pip show`.
        """
        try:
            metadata = PyPiManager._get_package_metadata(package_name)
            if not metadata:
                raise RuntimeError(f"Package {package_name} is not installed.")
            return metadata
        except Exception as e:
            raise RuntimeError(f"Failed to load package details for {package_name}: {e}")

    @staticmethod
    def _get_package_metadata(package_name: str) -> Dict[str, Any]:
        """
        Extracts metadata for an installed package using `pip show`.
        """
        # Ensure the custom install location is on sys.path
        if DEFAULT_RECIPE_INSTALL_LOCATION not in sys.path:
            sys.path.insert(0, DEFAULT_RECIPE_INSTALL_LOCATION)

        try:
            dist = importlib.metadata.distribution(package_name)
            # Convert it into a dictionary of metadata fields
            metadata_dict = {key.lower(): value for key, value in dist.metadata.items()}
            return metadata_dict
        except importlib.metadata.PackageNotFoundError:
            print(f"Package {package_name} not found in {DEFAULT_RECIPE_INSTALL_LOCATION}")
            return {}

    @staticmethod
    def _introspect_module(module_name: str) -> List[InstalledRecipe]:
        # Ensure the custom install location is on sys.path
        if DEFAULT_RECIPE_INSTALL_LOCATION not in sys.path:
            sys.path.insert(0, DEFAULT_RECIPE_INSTALL_LOCATION)

        # Convert to snake case per proper import conventions
        module_name = module_name.replace("-", "_")

        try:
            site.main()  # We want the recently installed module to be available to introspection
            module = importlib.import_module(module_name)
            submodules = [name for _, name, _ in pkgutil.iter_modules(module.__path__)]

            discovered_recipes: List[InstalledRecipe] = []

            for submodule in submodules:
                full_submodule_name = f"{module_name}.{submodule}"
                # Import each submodule
                sm = importlib.import_module(full_submodule_name)

                # Get all classes in the submodule
                classes = inspect.getmembers(sm, inspect.isclass)

                for class_name, class_obj in classes:
                    # Check if class is a subclass of Recipe
                    if issubclass(class_obj, Recipe) and class_obj is not Recipe:
                        discovered_recipes.append(
                            InstalledRecipe(
                                name=class_name,
                                source=full_submodule_name,
                                options=[],  # TODO support options
                            )
                        )

            return discovered_recipes
        except Exception as e:
            raise RuntimeError(f"Failed to introspect module {module_name}: {e}")

    @staticmethod
    def _package_exists_in_registry(
        index_url: str, package_name: str, version: Optional[str] = None
    ) -> bool:
        if not index_url.endswith("/"):
            index_url += "/"
        client = PyPISimple(endpoint=index_url)

        try:
            project_page = client.get_project_page(package_name)
            if not project_page:
                return False

            # When no version the presence of the package is enough to confirm a valid source
            if version is None:
                return True

            specifier = SpecifierSet(f"=={version}")

            # Hunt for a distribution that matches the requested version
            for dist in project_page.packages:
                if dist.version is not None:
                    dist_version = parse_version(dist.version)
                    if dist_version in specifier:
                        return True

            # No distributions matched the requested version specifier
            return False

        except Exception as e:  # pylint: disable=broad-except
            print(f"Error checking package {package_name}: {e}")
            return False

    @staticmethod
    def _get_authenticated_url(source: Source) -> str:
        """
        Returns the source URL with embedded authentication if username/password or token is provided.
        """
        if source.username and source.password:
            return source.source.replace(
                "https://", f"https://{source.username}:{source.password}@"
            )
        elif source.token:
            return source.source.replace("https://", f"https://{source.token}@")
        return source.source
