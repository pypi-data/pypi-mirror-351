from awslabs.cfn_mcp_server.errors import ServerError


class Context:
    """A singleton which includes context for the MCP server such as startup parameters."""

    _instance = None

    def __init__(self, readonly_mode: bool):
        """Initializes the context."""
        self._readonly_mode = readonly_mode

    @classmethod
    def readonly_mode(cls) -> bool:
        """If a the server was started up with the argument --readonly True, this will be set to True."""
        if cls._instance is None:
            raise ServerError('Context was not initialized')
        return cls._instance._readonly_mode

    @classmethod
    def initialize(cls, readonly_mode: bool):
        """Create the singleton instance of the type."""
        cls._instance = cls(readonly_mode)
