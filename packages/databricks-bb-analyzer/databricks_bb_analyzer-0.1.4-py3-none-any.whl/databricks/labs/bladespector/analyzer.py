import logging
import os
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

logger = logging.getLogger(__name__)

_PLATFORM_TO_SOURCE_TECHNOLOGY = {
    "ADF": "ADF",
    "Datastage": "DATASTAGE",
    "Informatica - Big Data Edition": "INFADEV",
    "Informatica - Desktop": "INFA",
    "SAS": "SAS",
    "SQL": "SQL",
    "SSIS": "SSIS",
    "Talend": "TALEND",
}

class Analyzer:

    @classmethod
    def supported_source_technologies(cls) -> list[str]:
        return list(_PLATFORM_TO_SOURCE_TECHNOLOGY.keys())

    @classmethod
    def analyze(cls, directory: Path, result: Path, platform: str):
        technology = _PLATFORM_TO_SOURCE_TECHNOLOGY.get(platform, None)
        if not technology:
            raise ValueError(f"Unsupported platform: {platform}")
        analyzer = Analyzer()
        analyzer._run_binary(directory, result, technology)

    def __init__(self):
        self._binary = self._locate_binary()

    def _run_binary(self, directory: Path, result: Path, technology: str):
        try:
            args = [
                str(self._binary),
                "-d",
                f"{directory}",
                "-r",
                f"{result}",
                "-t",
                technology,
                "-v",
            ]
            env = deepcopy(os.environ)
            env["UTF8_NOT_SUPPORTED"] = str(1)

            logger.info(f"Running command: {' '.join(args)}")

            # Use context manager for subprocess.Popen
            # TODO: Handle stdout and stderr properly (async/threads) to avoid pipe buffer blocking.
            with subprocess.Popen(
                args,
                env=env,
                stdout=None,
                stderr=None,
                text=True,
                bufsize=1,
                universal_newlines=True
            ) as process:
                process.wait()
                if process.returncode != 0:
                    raise subprocess.CalledProcessError(process.returncode, args)

            return None
        # it is good practice to catch broad exceptions raised by launching a child process
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Conversion failed", exc_info=e)
            return str(e)

    def _locate_binary(self) -> Path:
        if 'darwin' in sys.platform:
            tool = "MacOS/analyzer"
        elif 'win' in sys.platform:
            tool = "Windows/analyzer.exe"
        elif 'linux' in sys.platform:
            tool = "Linux/analyzer"
        else:
            raise Exception(f"Unsupported platform: {sys.platform}")
        return Path(__file__).parent / "Analyzer" / tool
