from dataclasses import dataclass
from typing import Dict, Union, Callable, Any

from .schema.service_info import ServiceInfo
from .use_case_code_inspector.use_case_code_metadata import UseCaseCodeInfo


@dataclass
class ServiceInfoWithCode:
    """Combines user-declared service metadata with use cases discovered in the source code.

    This structure is used to validate, align, or document the service definition by comparing
    declared metadata against the actual implementation found in code.

    Attributes
    ----------
    declared_metadata : ServiceInfo
        The service information provided explicitly by the user (e.g., via a YAML or JSON spec).
    discovered_use_cases : Dict[str, UseCaseCodeInfo]
        Use cases detected from the source code implementation.
    """
    declared_metadata: ServiceInfo
    discovered_use_cases: Dict[str, Union[UseCaseCodeInfo, Callable[..., Any]]]
