"""
This package is actually added as a parent package
because of the mypy limitation.
"""

# from . import application, domain, presentation  # noqa: F401


""" Bot """
__version__ = '2024.1-dev'

if 'dev' in __version__:
    from pathlib import Path
    try:
        import subprocess
        basedir = Path(__file__).parent

        __version__ = __version__ + '-' + subprocess.check_output(
            ['git', 'log', '--format="%h"', '-n 1'],
            stderr=subprocess.DEVNULL, cwd=basedir).decode("utf-8").rstrip().strip('"')

    except Exception:  # pragma: no cover
        # git not available, ignore
        try:
            # Try Fallback to last_commit file (created by CI while building docker image)
            versionfile = Path('./last_commit')
            if versionfile.is_file():
                __version__ = f"docker-{__version__}-{versionfile.read_text()[:8]}"
        except Exception:
            pass
