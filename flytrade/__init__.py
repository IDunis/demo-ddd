""" Flytrade bot """
__version__ = '2024.1-dev'

if 'dev' in __version__:
    from pathlib import Path
    try:
        import subprocess
        _basedir = Path(__file__).parent

        __version__ = __version__ + '-' + subprocess.check_output(
            ['git', 'log', '--format="%h"', '-n 1'],
            stderr=subprocess.DEVNULL, cwd=_basedir).decode("utf-8").rstrip().strip('"')

    except Exception:  # pragma: no cover
        # git not available, ignore
        try:
            # Try Fallback to flytrade_commit file (created by CI while building docker image)
            version_file = Path('./flytrade_commit')
            if version_file.is_file():
                __version__ = f"docker-{__version__}-{version_file.read_text()[:8]}"
        except Exception:
            pass
