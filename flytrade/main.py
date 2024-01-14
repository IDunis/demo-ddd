#!/usr/bin/env python3
"""
Main Flytrade bot script.
Read the documentation to know what cli arguments you need.
"""
import logging
import sys
from typing import Any, List, Optional

from flytrade.util.gc_setup import gc_set_threshold


# check min. python version
if sys.version_info < (3, 9):  # pragma: no cover
    sys.exit("Flytrade requires Python version >= 3.9")

from flytrade import __version__
from flytrade.commands import Arguments
from flytrade.exceptions import FlytradeException, OperationalException
from flytrade.loggers import setup_logging_pre


logger = logging.getLogger('flytrade')


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
        if 'func' in args:
            logger.info(f'flytrade {__version__}')
            gc_set_threshold()
            return_code = args['func'](args)
        else:
            # No subcommand was issued.
            raise OperationalException(
                "Usage of Flytrade requires a subcommand to be specified.\n"
                "To have the bot executing trades in live/dry-run modes, "
                "depending on the value of the `dry_run` setting in the config, run Flytrade "
                "as `flytrade trade [options...]`.\n"
                "To see the full list of options available, please use "
                "`flytrade --help` or `flytrade <command> --help`."
            )

    except SystemExit as e:  # pragma: no cover
        return_code = e
    except KeyboardInterrupt:
        logger.info('SIGINT received, aborting ...')
        return_code = 0
    except FlytradeException as e:
        logger.error(str(e))
        return_code = 2
    except Exception:
        logger.exception('Fatal exception!')
    finally:
        sys.exit(return_code)


if __name__ == '__main__':  # pragma: no cover
    main()
