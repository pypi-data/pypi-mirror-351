from __future__ import annotations

import io
import logging
import tarfile
import zipfile
from typing import TYPE_CHECKING, Any, TypedDict

from pydantic import BaseModel

from hud.server.requests import make_request
from hud.settings import settings

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

logger = logging.getLogger("hud.utils.common")


class FunctionConfig(BaseModel):
    function: str  # Format: "x.y.z"
    args: list[Any]  # Must be json serializable

    id: str | None = None  # Optional id for remote execution
    metadata: dict[str, Any] | None = None  # Optional metadata for telemetry

    def __len__(self) -> int:
        return len(self.args)

    def __getitem__(self, index: int) -> Any:
        return self.args[index]

    def __iter__(self) -> Iterator[Any]:
        return iter(self.args)

    def __str__(self) -> str:
        return f"FC: {self.function}: {', '.join(str(arg) for arg in self.args)} ({self.metadata})"


# Type alias for the shorthand config, which just converts to function name and args
BasicType = str | int | float | bool | None
ShorthandConfig = tuple[BasicType | dict[str, Any] | list[BasicType] | list[dict[str, Any]], ...]

# Type alias for multiple config formats
FunctionConfigs = (
    ShorthandConfig
    | FunctionConfig
    | list[FunctionConfig]
    | list[ShorthandConfig]
    | dict[str, Any]
    | str
)


class Observation(BaseModel):
    """
    Observation from the environment.

    Attributes:
        screenshot: Base64 encoded PNG string of the screen
        text: Text observation, if available
    """

    screenshot: str | None = None  # base64 string png
    text: str | None = None

    def __str__(self) -> str:
        return f"""Observation(screenshot={
            self.screenshot[:100] if self.screenshot else "None"
        }..., text={self.text}...)"""


class ExecuteResult(TypedDict):
    """
    Result of an execute command.

    Attributes:
        stdout: Standard output from the command
        stderr: Standard error from the command
        exit_code: Exit code of the command
    """

    stdout: bytes
    stderr: bytes
    exit_code: int


def directory_to_tar_bytes(directory_path: Path) -> bytes:
    """
    Converts a directory to a tar archive and returns it as bytes.

    This function creates a tar archive of the specified directory in memory,
    without writing to a temporary file on disk.

    Args:
        path: Path to the directory to convert

    Returns:
        Bytes of the tar archive
    """
    output = io.BytesIO()

    with tarfile.open(fileobj=output, mode="w") as tar:
        # Walk through the directory
        for file_path in directory_path.rglob("*"):
            if file_path.is_file():
                # Calculate relative path for the archive
                rel_path = file_path.relative_to(directory_path)
                logger.debug("Adding %s to tar archive", rel_path)
                tar.add(file_path, arcname=str(rel_path))

    # Get the bytes from the BytesIO object
    output.seek(0)
    return output.getvalue()


def directory_to_zip_bytes(context_dir: Path) -> bytes:
    """Zip a directory and return the zip archive as bytes."""
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in context_dir.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(context_dir)
                logger.debug("Adding %s to zip archive", rel_path)
                zipf.write(str(file_path), arcname=str(rel_path))
    return output.getvalue()


async def get_gym_id(gym_name_or_id: str) -> str:
    """
    Get the gym ID for a given gym name or ID.
    """
    data = await make_request(
        method="GET",
        url=f"{settings.base_url}/v1/gyms/{gym_name_or_id}",
        api_key=settings.api_key,
    )

    return data["id"]
