# Copyright (c) 2024, qBraid Development Team
# All rights reserved.

"""
Script to anaylze disk usage and report to computer manger.

"""

import asyncio
import json
import logging
import os
import subprocess
import threading
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

import tornado
from jupyter_server.base.handlers import APIHandler
from qbraid_core import QbraidException, QbraidSession

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)


class Unit(str, Enum):
    """Enum to represent the units of disk usage."""

    KB = "KB"
    MB = "MB"
    GB = "GB"

    @classmethod
    def from_str(cls, unit: str) -> "Unit":
        """Create a Unit from a string."""
        try:
            return cls(unit.upper())
        except ValueError as e:
            raise ValueError(f"Invalid unit: {unit}") from e


CONVERSION_FACTORS = {
    Unit.KB: Decimal("1000000"),
    Unit.MB: Decimal("1000"),
    Unit.GB: Decimal("1"),
}


def convert_to_gb(size: Decimal, unit: Unit) -> Decimal:
    """
    Converts a size in a given unit to GB.

    Args:
        size (Decimal): The size value to convert.
        unit (Unit): The unit of the size.

    Returns:
        Decimal: The size in GB.

    Raises:
        ValueError: If the unit is not recognized.
    """
    if unit not in CONVERSION_FACTORS:
        raise ValueError(f"Unknown unit: {unit}")
    return size / CONVERSION_FACTORS[unit]


async def get_disk_usage_gb(filepath: Optional[Union[str, Path]] = None) -> Decimal:
    """
    Get the disk usage of a file or directory in GB.

    Args:
        filepath (Optional[Union[str, Path]]): The file or directory path to measure.

    Returns:
        Decimal: The disk usage in GB.

    Raises:
        RuntimeError: If there are errors executing or parsing the command output.
        FileNotFoundError: If the file or directory does not exist.
    """
    try:
        command = ["gdu", "-p", "-n", "-s", "--si"]

        if filepath:
            filepath = Path(filepath)
            if not filepath.exists():
                raise FileNotFoundError(f"File or directory does not exist: {filepath}")
            command.append(str(filepath))

        # Create subprocess
        process = await asyncio.create_subprocess_exec(
            *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        # Wait for the process to complete and capture output
        stdout, stderr = await process.communicate()

        # Decode and return output
        if process.returncode == 0:
            value, unit_str = stdout.decode().strip().split()[:2]
            # logger.info(f"Disk usage command output: Value = {value}, Unit = {unit_str}")
            unit = Unit.from_str(unit_str)
            gb = convert_to_gb(Decimal(value), unit)
            gb_rounded = gb.quantize(Decimal("0.01"))
            return gb_rounded
        else:
            raise Exception(f"Error executing command: {stderr.decode().strip()}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error executing gdu: {e}") from e
    except (ValueError, IndexError) as e:
        raise RuntimeError(f"Error processing gdu output: {e}") from e


async def report_disk_usage(total_gb: Decimal) -> dict[str, Any]:
    """
    Report the disk usage to the qBraid API.

    Args:
        total_gb (Decimal): The total disk usage in GB.

    Returns:
        dict[str, Any]: The response data from the API.

    Raises:
        RuntimeError: If there are errors reporting the disk usage or decoding the response.
    """
    try:
        session = QbraidSession()
        response = session.put("/user/disk-usage", json={"totalGB": float(total_gb)})
        return response.json()
    except QbraidException as e:
        raise RuntimeError(f"Error reporting disk usage: {e}") from e
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Error decoding response: {e}") from e


async def update_values():
    try:
        home = Path.home()
        """Run the disk usage report."""
        total_gb = await get_disk_usage_gb(home)
        total_gb = float(total_gb)
        """ once the disk usage is available, call the put api to update the disk usage."""
        response = await report_disk_usage(total_gb)
    except Exception as e:
        raise RuntimeError(f"Error updating values: {e}") from e


class DiskUsageHandler(APIHandler):
    """Handler for managing user configurations and other local data."""

    @tornado.web.authenticated
    async def put(self):
        """Get disk usage for a users home directory."""

        response_data = {"status": 202, "message": "Disk usage reporting initiated successfully"}

        try:
            asyncio.create_task(update_values())
        except RuntimeError as e:
            logger.error("Error reporting disk usage: %s", e)
            response_data = {"status": 500, "error": str(e)}
        except ValueError as e:
            logger.error("Invalid input: %s", e)
            response_data = {"status": 500, "error": str(e)}
        except Exception as e:
            logger.error("Error getting disk usage: %s", e)
            response_data = {"status": 500, "error": str(e)}

        self.finish(json.dumps(response_data))
