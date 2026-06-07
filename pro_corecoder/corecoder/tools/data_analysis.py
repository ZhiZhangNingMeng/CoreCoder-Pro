"""
Dynamic data analysis sandbox tool.
Supports LLM writing Python code to run in an independent process for advanced computation using Pandas, Numpy, Scipy, etc.
"""

import os
import sys
import subprocess
import tempfile
from .base import Tool


class DataAnalysisTool(Tool):
    name = "data_analysis"
    description = (
        "Use this when you need to perform advanced statistics, pivoting, aggregation, and deep analysis "
        "on complex structured data (like CSV, Excel, or Dataframes). "
        "This sandbox runs in an independent Python process and has pandas, numpy, and scipy pre-installed.\n"
        "[CORE CODING RULES - DO NOT VIOLATE]:\n"
        "1. You must write complete, independently executable Python source code.\n"
        "2. You must use the built-in print() function to output the final data analysis conclusions or key metrics, otherwise the tool returns nothing.\n"
        "3. DO NOT write any plotting code (e.g., matplotlib, seaborn), do not attempt to output or display chart objects, and do not save image files.\n"
        "4. Security constraints are enforced. It is strictly forbidden to import any modules involving low-level system modifications or network communication (e.g., os, subprocess, shutil, socket, etc.)."
    )
    parameters = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The complete Python source code string to be executed in the isolated sandbox process."
            }
        },
        "required": ["code"]
    }

    def execute(self, code: str) -> str:
        # 1. Security interception: Static check for basic sensitive keywords and high-risk modules
        forbidden_patterns = [
            "import os", "from os",
            "import subprocess", "from subprocess",
            "import shutil", "from shutil",
            "import sys", "from sys",
            "import pty", "import socket",
            "import requests", "import urllib",
            "eval(", "exec(", "open(", "compile(", "__import__", "builtins"
        ]

        cleaned_code = code.strip()
        for pattern in forbidden_patterns:
            if pattern in cleaned_code:
                return (
                    f"Security Restriction Warning: Detected forbidden system-level operations or modules '{pattern}'. "
                    f"This sandbox only allows pure data computation (Pandas, Numpy, Scipy, etc.). "
                    f"Please regenerate the code without violating operations."
                )

        temp_file_path = None
        try:
            # 2. Isolated execution: Use tempfile to create a safe temporary .py file
            # delete=False ensures we can read it in the subsequent subprocess
            with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w", encoding="utf-8") as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name

            # 3. Timeout and fault tolerance: Launch independent process to execute
            # Using sys.executable ensures the subprocess reuses the dependencies (Pandas, etc.) in the current CoreCoder virtual environment
            result = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=60  # 60-second hard timeout limit
            )

            # Merge output results
            output_segments = []
            if result.stdout:
                output_segments.append("--- Standard Output (stdout) ---")
                output_segments.append(result.stdout)
            if result.stderr:
                # When the code crashes, Python interpreter automatically spits the Traceback to stderr
                output_segments.append("--- Error Traceback (stderr) ---")
                output_segments.append(result.stderr)

            if not output_segments:
                return "Code executed successfully, but the console produced no output. Please check if you forgot to use print() to output the final result."

            return "\n".join(output_segments)

        except subprocess.TimeoutExpired:
            return "Execution Error: The Python code exceeded the 60-second hard time limit. Please optimize your algorithm, avoid infinite loops, or reduce the dataset size."
        except Exception as e:
            return f"Sandbox system execution exception: {str(e)}"

        finally:
            # 5. Cleanup mechanism: Always delete the temporary file whether it succeeds, fails, or times out
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception:
                    pass  # Tolerate occasional exceptions during cleanup