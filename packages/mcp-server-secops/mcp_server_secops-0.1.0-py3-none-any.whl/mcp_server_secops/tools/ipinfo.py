import subprocess
import json
from typing import Optional


def run_ipinfo(
    ip: str,
    json_output: Optional[bool] = True
) -> str:
    """Run ipinfo lookup on a given IP address.

    Args:
        ip: The IP address to look up
        json_output: Whether to request JSON-formatted output

    Returns:
        str: JSON string with lookup results or error
    """
    try:
        # Build command
        cmd = ["ipinfo", ip]

        # Execute
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        return json.dumps({
            "success": True,
            "ip": ip,
            "results": result.stdout.strip()
        })

    except subprocess.CalledProcessError as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "stderr": e.stderr.strip()
        })
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        })