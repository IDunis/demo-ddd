#!/usr/bin/env python3
"""
Main Trapilot bot script.
Read the documentation to know what cli arguments you need.
"""
import logging
import sys
from typing import Any, List, Optional

from trapilot.LIB.util.gc_setup import gc_set_threshold

# check min. python version
if sys.version_info < (3, 9):  # pragma: no cover
    sys.exit("Trapilot requires Python version >= 3.9")

from trapilot.LIB import __version__
from trapilot.LIB.commands import Arguments
from trapilot.LIB.exceptions import FreqtradeException, OperationalException
from trapilot.LIB.loggers import setup_logging_pre

logger = logging.getLogger("trapilot")


def main(sysargv: Optional[List[str]] = None) -> None:
    """
    This function will initiate the bot and start the trading loop.
    :return: None
    """

    return_code: Any = 1
    try:
        setup_logging_pre()
        arguments = Arguments(sysargv)
        args = arguments.get_parsed_arg()

        # Call subcommand.
        if "func" in args:
            logger.info(f"trapilot {__version__}")
            gc_set_threshold()
            return_code = args["func"](args)
        else:
            # No subcommand was issued.
            raise OperationalException(
                "Usage of Trapilot requires a subcommand to be specified.\n"
                "To have the bot executing trades in live/dry-run modes, "
                "depending on the value of the `dry_run` setting in the config, run Trapilot "
                "as `trapilot trade [options...]`.\n"
                "To see the full list of options available, please use "
                "`trapilot --help` or `trapilot <command> --help`."
            )

    except SystemExit as e:  # pragma: no cover
        return_code = e
    except KeyboardInterrupt:
        logger.info("SIGINT received, aborting ...")
        return_code = 0
    except FreqtradeException as e:
        logger.error(str(e))
        return_code = 2
    except Exception:
        logger.exception("Fatal exception!")
    finally:
        sys.exit(return_code)


if __name__ == "__main__":  # pragma: no cover
    main()
