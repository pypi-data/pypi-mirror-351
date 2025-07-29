from __future__ import annotations

from pathlib import Path
from typing import Any
from zipfile import ZipFile

from fused.models.udf import AnyBaseUdf

from .._str_utils import is_uuid
from ._impl._context_impl import context_get_user_email
from ._impl._udf_ops_impl import (
    get_github_udf_from_server,
    get_step_config_from_server,
    get_step_config_from_shared_token,
    get_udf_from_code,
    get_udf_from_directory,
    get_udf_from_file,
)


def load_udf_from_fused(
    email_or_handle_or_id: str, id: str | None = None, *, cache_key: Any = None
) -> AnyBaseUdf:
    """
    Download the code of a UDF, to be run inline.

    Args:
        email_or_handle_or_id: Email or handle of the UDF's owner, or name of the UDF to import.
        id: Name of the UDF to import. If only the first argument is provided, the current user's email will be used.

    Keyword args:
        cache_key: Additional cache key for busting the UDF cache
    """
    if id is None and not is_uuid(email_or_handle_or_id):
        id = email_or_handle_or_id
        try:
            email_or_handle = context_get_user_email()
        except Exception as e:
            raise ValueError(
                "could not detect user ID from context, please specify the UDF as 'user@example.com' (or 'user'), 'udf_name'."
            ) from e
    else:
        email_or_handle = email_or_handle_or_id
    step_config = get_step_config_from_server(
        email_or_handle=email_or_handle,
        slug=id,
        cache_key=cache_key,
    )

    return step_config.udf


def load_udf_from_github(url: str, *, cache_key: Any = None) -> AnyBaseUdf:
    """
    Download the code of a UDF, to be run inline.

    Args:
        email_or_id: Email of the UDF's owner, or name of the UDF to import.
        id: Name of the UDF to import. If only the first argument is provided, the current user's email will be used.

    Keyword args:
        cache_key: Additional cache key for busting the UDF cache
    """
    step_config = get_github_udf_from_server(url=url, cache_key=cache_key)

    return step_config.udf


def load_udf_from_shared_token(token: str) -> AnyBaseUdf:
    """
    Download the code of a UDF from a shared token

    Args:
        token: the shared token for a UDF

    Raises:
        requests.HTTPError if the token is for a UDF that is not owned by the current user
    """
    return get_step_config_from_shared_token(token).udf


def load_udf_from_file(path: Path) -> AnyBaseUdf:
    """
    Load a UDF from a python file

    Args:
        path : pathlib.Path
    """
    return get_udf_from_file(path)


def load_udf_from_directory(path: Path) -> AnyBaseUdf:
    """
    Load a UDF from a python file

    Args:
        path : pathlib.Path
    """

    def _load_file(name: str) -> bytes:
        file_path = path / name
        if not file_path.exists():
            raise ValueError(
                f"Expected a file to be at {repr(file_path)}. Is this the right directory to load from?"
            )

        return file_path.read_bytes()

    return get_udf_from_directory(load_callback=_load_file)


def load_udf_from_zip(path: Path) -> AnyBaseUdf:
    """
    Load a UDF from a python file

    Args:
        path : pathlib.Path
    """
    with ZipFile(path) as zf:
        return get_udf_from_directory(load_callback=lambda f: zf.read(f))


def load_udf_from_code(code: str) -> AnyBaseUdf:
    """
    Load a UDF from raw code.

    """
    return get_udf_from_code(code)
