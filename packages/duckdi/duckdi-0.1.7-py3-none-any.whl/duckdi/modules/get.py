from duckdi.errors.invalid_adapter_implementation_error import InvalidAdapterImplementationError
from duckdi.modules.injections_container import InjectionsContainer
from duckdi.modules.injections_payload import InjectionsPayload
from duckdi.utils.serializers import to_snake
from typing import Optional, Type


def Get[T](interface: Type[T], label: Optional[str] = None) -> T:
    """
    # Resolves and returns an instance of the adapter associated with the given interface.
    # This function is the main entry point for resolving dependencies no runtime.

    # Args:
        - interface (Type[T]): The interface class decorated with @Interface.
        - label (Optional[str]): Optional custom label used during interface registration. If omitted, the snake_case name of the interface class is used.

    # Returns:
        - T: An instance of the adapter class bound to the interface.

    # Raises
        - KeyError: If the interface is not found in the injection payload.
        - InvalidAdapterImplementationError: If the resolved adapter does not implement the expected interface.

    # Example:
    .   @Interface
    .   class IUserRepository:
    .       ...
    .
    .   register(PostgresUserRepository)
    .   user_repo = Get(IUserRepository)
    """
    injections_payload = InjectionsPayload().load()
    interface_name = label if label is not None else to_snake(interface)
    adapter = InjectionsContainer.adapters[injections_payload[interface_name]]

    if not isinstance(adapter, type):
        if not isinstance(adapter, interface):
            raise InvalidAdapterImplementationError(
                interface.__name__, type(adapter).__name__
            )
        return adapter

    if not issubclass(adapter, interface):
        raise InvalidAdapterImplementationError(interface.__name__, adapter.__name__)

    return adapter()
