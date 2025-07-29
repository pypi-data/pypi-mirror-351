import ast
import time
import warnings
from contextlib import ExitStack
from typing import Any

import fused
from fused._optional_deps import HAS_PANDAS, PD_DATAFRAME
from fused._udf.compile_v2 import compile_udf_and_run_with_kwargs
from fused._udf.state import (
    _isolate_streams,
    decorator_src_override_context,
)
from fused.models.schema import Schema
from fused.models.udf import EMPTY_UDF, AnyBaseUdf, Output, PandasOutput
from fused.models.udf._eval_result import UdfEvaluationResult
from fused.warnings import FusedWarning


def execute_against_sample(
    udf: AnyBaseUdf,
    input: list[Any],
    update_schema: bool = True,
    validate_output: bool = True,
    validate_imports: bool | None = None,
    _return_response: bool = False,
    **kwargs,
) -> UdfEvaluationResult:
    if udf is EMPTY_UDF:
        raise ValueError("Empty UDF cannot be evaluated. Use `set_udf` to set a UDF.")

    output = Output()
    try:
        # Validate import stamements correspond to valid modules
        validate_imports_whitelist(udf, validate_imports=validate_imports)

        # Run UDF
        if _return_response:
            # TODO capture output
            _output = None
            has_exception = False
            errormsg = None
            exception_class = None
            time_start = time.perf_counter()
            try:
                _output = compile_udf_and_run_with_kwargs(udf, *input, **kwargs)
            except Exception as exc:
                has_exception = True
                exception_class = exc.__class__.__name__
                errormsg = f"{exception_class}: {str(exc)}"
                # TODO proper error traceback
                # traceback.print_tb(exc.__traceback__, file=err_buf)
            time_end = time.perf_counter()
            time_taken_seconds = time_end - time_start

            return UdfEvaluationResult(
                data=_output,
                udf=udf,
                time_taken_seconds=time_taken_seconds,
                stdout=None,
                stderr=None,
                error_message=errormsg,
                has_exception=has_exception,
                exception_class=exception_class,
            )

        time_start = time.perf_counter()
        with _isolate_streams():
            _output = compile_udf_and_run_with_kwargs(udf, *input, **kwargs)
        time_end = time.perf_counter()
        time_taken_seconds = time_end - time_start

        if not validate_output:
            return _output

        if _output is not None:
            output.data = _output

    except Exception:
        raise

    new_output = _transform_output(output=output)

    if new_output is None:
        # TODO: Assumes table_schema is present, which doesn't match type
        if udf.table_schema not in [None, {}, Schema()]:
            warnings.warn(
                FusedWarning(
                    "UDF is configured with a schema but returns `None`. An empty schema was set for this execution."
                )
            )

        return UdfEvaluationResult(
            data=None,
            sidecar=None,
            udf=udf,
            table_schema={},
            time_taken_seconds=time_taken_seconds,
        )

    # Validate the dataframe after assigning it to the output variable in user_ns
    # so the user can inspect the output if anything is wrong.
    new_output.validate_data_with_schema()

    if update_schema and udf.table_schema is None:
        udf.table_schema = new_output.table_schema

    return UdfEvaluationResult(
        data=new_output.data,
        sidecar=new_output.sidecar_output,
        udf=udf,
        table_schema=new_output.table_schema,
        time_taken_seconds=time_taken_seconds,
    )


def execute_for_decorator(udf: AnyBaseUdf) -> AnyBaseUdf:
    """Evaluate a UDF for the purpose of getting the UDF object out of it."""
    # Define custom function in environment

    # This is a stripped-down version of execute_against_sample, above.

    src = udf.code

    exec_globals_locals = {"fused": fused}

    with ExitStack() as stack:
        stack.enter_context(decorator_src_override_context(src))

        # Add headers to sys.meta_path
        if udf.headers is not None:
            for header in udf.headers:
                stack.enter_context(header._register_custom_finder())

        exec(src, exec_globals_locals, exec_globals_locals)

        if udf.entrypoint not in exec_globals_locals:
            raise NameError(
                f"Could not find {udf.entrypoint}. You need to define a UDF with `def {udf.entrypoint}()`."
            )

        _fn = exec_globals_locals[udf.entrypoint]

        return _fn


def _transform_output(output: Output) -> PandasOutput:
    # TODO: Support PyArrow
    if isinstance(output, PandasOutput):
        return output

    if HAS_PANDAS and isinstance(output.data, PD_DATAFRAME):
        # Force all column names to be strings
        output.data.columns = [str(x) for x in output.data.columns]

        # Note that we don't pass a _new_ schema argument here
        # - If the user defined a schema onto output.table_schema, that will be
        #   preserved.
        # - If the user did not define output.table_schema, then output.table_schema
        #   will be None, and PandasOutput will default to a schema inferred from
        #   the DataFrame.
        return PandasOutput(
            data=output.data,
            table_schema=output.table_schema,
            sidecar_output=output.sidecar_output,
            skip_fused_index_validation=output.skip_fused_index_validation,
        )
    elif output.data is None:
        return None

    raise TypeError(f"Unexpected result type {type(output.data)}")


def validate_imports_whitelist(udf: AnyBaseUdf, validate_imports: bool | None = None):
    # Skip import validation if the option is set
    if not fused.options.default_validate_imports and validate_imports is not True:
        return

    # Skip import validation if not logged in
    if not fused.api.AUTHORIZATION.is_configured():
        return

    from fused._global_api import get_api

    # Get the dependency whitelist from the cached API endpoint
    api = get_api()
    package_dependencies = api.dependency_whitelist()

    # Initialize a list to store the import statements
    import_statements = []

    # Parse the source code into an AST
    tree = ast.parse(udf.code)

    # Traverse the AST to find import statements
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_statements.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module
            import_statements.append(module_name)

    # Check for unavailable modules
    header_modules = [header.module_name for header in udf.headers]
    fused_modules = ["fused"]  # assume fused is always available
    available_modules = (
        list(package_dependencies["dependency_whitelist"].keys())
        + header_modules
        + fused_modules
    )
    unavailable_modules = []
    for import_statement in import_statements:
        if import_statement.split(".", 1)[0] not in available_modules:
            unavailable_modules.append(import_statement)

    if unavailable_modules:
        raise ValueError(
            f"The following imports in the UDF might not be available: {repr(unavailable_modules)}. Please check the UDF headers and imports and try again."
        )

    # TODO: check major versions for some packages
