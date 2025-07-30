"""MyPy plugin for schemix type checking."""

from collections.abc import Callable

from mypy.plugin import MethodSigContext, Plugin
from mypy.types import CallableType


def plugin(version: str) -> type[Plugin]:
    """Entry point for mypy plugin."""
    return SchemixPlugin


class SchemixPlugin(Plugin):
    """Main plugin class for schemix type checking."""

    def get_method_signature_hook(
        self, fullname: str
    ) -> Callable[[MethodSigContext], CallableType] | None:
        """Hook for method signature analysis."""
        if fullname == "schemix.database.Database.select":
            return self.select_signature_hook
        return None

    def select_signature_hook(self, ctx: MethodSigContext) -> CallableType:
        """Handle Database.select() method signature."""
        # Analyze the dictionary argument to create a proper return type
        from .select_handler import create_signature_with_typed_dict

        return create_signature_with_typed_dict(ctx)
