"""Handler for Database.select() method type inference."""

from mypy.nodes import DictExpr, StrExpr
from mypy.plugin import MethodSigContext
from mypy.types import AnyType, CallableType, TypedDictType, TypeOfAny
from mypy.types import Type as MyPyType


def create_signature_with_typed_dict(ctx: MethodSigContext) -> CallableType:
    """
    Create a new method signature that accepts dict[str, Any] and returns SelectBuilder[TypedDict].

    This analyzes the dictionary argument and creates a specific TypedDict return type.
    """

    # Get the dictionary expression from the call
    if ctx.args and len(ctx.args[0]) > 0:
        first_arg = ctx.args[0][0]
        if isinstance(first_arg, DictExpr):
            # Try to create TypedDict from the dictionary expression
            typed_dict = _create_typed_dict_from_dict_expr_sig(ctx, first_arg)
            if typed_dict is not None:
                # Create flexible input type that accepts dict[str, Any]
                dict_type = ctx.api.named_generic_type(
                    "builtins.dict",
                    [
                        ctx.api.named_generic_type("builtins.str", []),
                        AnyType(TypeOfAny.special_form),
                    ],
                )

                # Create SelectBuilder[TypedDict] return type
                # Use the existing return type as template but substitute the type argument
                from mypy.types import Instance

                original_ret_type = ctx.default_signature.ret_type
                if isinstance(original_ret_type, Instance):
                    select_builder_type = original_ret_type.copy_modified(
                        args=[typed_dict]
                    )
                else:
                    select_builder_type = original_ret_type

                # Create new signature
                new_signature = ctx.default_signature.copy_modified(
                    arg_types=[dict_type], ret_type=select_builder_type
                )

                return new_signature

    # Fall back to default behavior but make input more permissive
    dict_type = ctx.api.named_generic_type(
        "builtins.dict",
        [
            ctx.api.named_generic_type("builtins.str", []),
            AnyType(TypeOfAny.special_form),
        ],
    )

    new_signature = ctx.default_signature.copy_modified(arg_types=[dict_type])

    return new_signature


def _create_typed_dict_from_dict_expr_sig(
    ctx: MethodSigContext, dict_expr: DictExpr
) -> MyPyType | None:
    """
    Create a TypedDict type from a dictionary expression in method signature context.
    """
    if not dict_expr.items:
        return None

    # Extract field names and types
    field_names = []
    field_types = []

    for key_node, value_node in dict_expr.items:
        # Extract field name from string literal
        if isinstance(key_node, StrExpr):
            field_name = key_node.value
        else:
            # If key is not a string literal, fall back to None
            return None

        # Extract column type from the value expression
        column_type = _get_column_type_from_expr_sig(ctx, value_node)
        if column_type is None:
            # If we can't determine the column type, fall back to None
            return None

        field_names.append(field_name)
        field_types.append(column_type)

    # Create TypedDict
    try:
        # Create the actual TypedDict instance
        fallback = ctx.api.named_generic_type(
            "builtins.dict",
            [
                ctx.api.named_generic_type("builtins.str", []),
                ctx.api.named_generic_type("builtins.object", []),
            ],
        )

        typed_dict = TypedDictType(
            items=dict(zip(field_names, field_types, strict=False)),
            required_keys=set(field_names),
            fallback=fallback,
            readonly_keys=set(),
            line=-1,
        )

        return typed_dict

    except Exception:
        # Silently fail and return None
        return None


def _get_column_type_from_expr_sig(ctx: MethodSigContext, expr) -> MyPyType | None:
    """
    Extract the Python type from a column expression in method signature context.
    """
    # Get the type of the expression
    try:
        expr_type = ctx.api.get_expression_type(expr)
    except Exception:
        return None

    # Map column types to Python types
    from mypy.types import Instance

    if (
        isinstance(expr_type, Instance)
        and hasattr(expr_type, "type")
        and hasattr(expr_type.type, "fullname")
    ):
        fullname = expr_type.type.fullname

        if fullname == "schemix.columns.VarChar":
            return ctx.api.named_generic_type("builtins.str", [])
        elif fullname == "schemix.columns.Integer":
            return ctx.api.named_generic_type("builtins.int", [])
        elif fullname and fullname.startswith("schemix.columns."):
            # For other column types, default to Any for now
            return AnyType(TypeOfAny.special_form)

    # If we can't determine the type, return None
    return None
