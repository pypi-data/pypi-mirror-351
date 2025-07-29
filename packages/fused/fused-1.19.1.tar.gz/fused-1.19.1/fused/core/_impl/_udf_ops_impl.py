import ast
import json
from pathlib import Path
from typing import Any, Callable, Optional

from loguru import logger

from fused._global_api import get_api
from fused.models._codegen import MetaJson
from fused.models.api import UdfJobStepConfig
from fused.models.udf import (
    GeoPandasUdfV2,
    load_udf_from_response_data,
)

try:
    from cachetools import TTLCache, cached

    memoize_cache = cached(TTLCache(maxsize=10240, ttl=60))
    logger.debug("cachetools TTL memoize cache initialized")
except ImportError:
    from functools import lru_cache

    # Number of entries to store
    memoize_cache = lru_cache(maxsize=1024)
    logger.debug("lru memoize cache initialized")


def get_step_config_from_server(
    email_or_handle: Optional[str],
    slug: str,
    cache_key: Any,
    _is_public: bool = False,
    import_udf_globals: bool = True,
) -> UdfJobStepConfig:
    logger.info(f"Requesting {email_or_handle=} {slug=}")
    # cache_key is unused
    api = get_api()
    if _is_public:
        obj = api._get_public_udf(slug)
    else:
        obj = api._get_udf(email_or_handle, slug)
    udf = load_udf_from_response_data(
        obj, context={"import_globals": import_udf_globals}
    )

    step_config = UdfJobStepConfig(udf=udf)
    return step_config


@memoize_cache
def get_github_udf_from_server(url: str, *, cache_key: Any = None) -> UdfJobStepConfig:
    logger.info(f"Requesting {url=}")
    # cache_key is unused
    api = get_api(credentials_needed=False)
    obj = api._get_code_by_url(url)
    udf = load_udf_from_response_data(obj)

    step_config = UdfJobStepConfig(udf=udf)
    return step_config


def get_step_config_from_shared_token(token: str) -> UdfJobStepConfig:
    api = get_api()
    obj = api._get_udf_by_token(token)
    udf = load_udf_from_response_data(obj)
    return UdfJobStepConfig(udf=udf)


def get_udf_from_file(path: Path) -> GeoPandasUdfV2:
    data = {
        "name": path.stem,
        "entrypoint": "udf",
        "type": "geopandas_v2",
        "code": path.read_bytes().decode("utf8"),
    }
    return GeoPandasUdfV2.model_validate(data)


def _get_entrypoint_of_code(code: str):
    """
    Returns the name of the function decorated with '@fused.udf' in the provided code.
    If multiple functions are decorated with '@fused.udf', use "udf" as the entrypoint.
    """
    found_udf_names: list[str] = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    is_fused_udf = False
                    actual_decorator = decorator
                    # If the decorator is called (e.g., @fused.udf(arg=...)),
                    # the node is ast.Call, and the actual decorator is in .func
                    if isinstance(decorator, ast.Call):
                        actual_decorator = decorator.func

                    # Check for @fused.udf (Attribute)
                    if isinstance(actual_decorator, ast.Attribute):
                        if (
                            isinstance(actual_decorator.value, ast.Name)
                            and actual_decorator.value.id == "fused"
                            and actual_decorator.attr == "udf"
                        ):
                            is_fused_udf = True
                    # Check for @udf (Name, assuming `from fused import udf`)
                    elif (
                        isinstance(actual_decorator, ast.Name)
                        and actual_decorator.id == "udf"
                    ):
                        is_fused_udf = True

                    if is_fused_udf:
                        found_udf_names.append(node.name)
                        break  # Only need to find one relevant decorator per function

    except SyntaxError as e:
        raise ValueError(f"Invalid Python code provided: {e}") from e

    if not found_udf_names:
        raise ValueError(
            "No function decorated with '@fused.udf' found in the provided code."
        )
    elif len(found_udf_names) == 1:
        return found_udf_names[0]
    elif len(found_udf_names) > 1:
        if "udf" not in found_udf_names:
            raise ValueError(
                f"Multiple functions decorated with '@fused.udf' found: {', '.join(found_udf_names)}. "
                "Please provide code with only one decorated UDF."
            )
        else:
            return "udf"


def get_udf_from_code(code: str, name: Optional[str] = None) -> GeoPandasUdfV2:
    udf_entrypoint_name = _get_entrypoint_of_code(code)

    data = {
        "name": name or udf_entrypoint_name,  # Use found name as default
        "entrypoint": udf_entrypoint_name,  # Use found name as entrypoint
        "type": "geopandas_v2",
        "code": code,
    }
    return GeoPandasUdfV2.model_validate(data)


def get_udf_from_directory(load_callback: Callable[[str], bytes]) -> GeoPandasUdfV2:
    meta_contents = json.loads(load_callback("meta.json"))
    meta = MetaJson.model_validate(meta_contents)

    if len(meta.job_config.steps) != 1:
        raise ValueError(
            f"meta.json is not in expected format: {len(meta.job_config.steps)=}"
        )

    if meta.job_config.steps[0]["type"] != "udf":
        raise ValueError(
            f'meta.json is not in expected format: {meta.job_config.steps[0]["type"]=}'
        )

    # Load the source code into the UDF model
    udf_dict = meta.job_config.steps[0]["udf"]
    source_file_name = udf_dict["source"]

    code = load_callback(source_file_name).decode("utf-8")
    udf_dict["code"] = code
    del udf_dict["source"]

    # Do the same for headers
    for header_dict in udf_dict["headers"]:
        header_source_file_name = header_dict.get("source_file")
        if header_source_file_name:
            del header_dict["source_file"]
            header_code = load_callback(header_source_file_name).decode("utf-8")
            header_dict["source_code"] = header_code

    return GeoPandasUdfV2.model_validate(udf_dict)
