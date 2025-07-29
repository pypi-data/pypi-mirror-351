from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class PackageSource:
    source: str = ""
    credential: Optional[Dict[str, str]] = None


@dataclass
class RecipeOption:
    name: str
    type: str
    required: bool
    value: Optional[Any]


@dataclass
class Recipe:
    name: str
    source: str
    options: List[RecipeOption] = field(default_factory=list)


@dataclass
class RecipeInstallResponse:
    recipes: List[Recipe]
    repository: str
    version: str
