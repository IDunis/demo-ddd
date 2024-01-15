#!/usr/bin/env python3
"""
Main IBuzz bot script.
Read the documentation to know what cli arguments you need.
"""
import logging
import signal
import sys
from typing import Any,Dict, List, Optional

from src.util.gc_setup import gc_set_threshold


# check min. python version
if sys.version_info < (3, 9):  # pragma: no cover
    sys.exit("IBuzz requires Python version >= 3.9")

from src import __version__
from src.commands import Arguments
from src.exceptions import FreqtradeException, OperationalException
# from src.loggers import setup_logging_pre


logger = logging.getLogger('ibuzz')

def start_trading(args: Dict[str, Any]) -> int:
    """
    Main entry point for trading mode
    """
    # Import here to avoid loading worker module when it's not used
    from src.worker import Worker

    def term_handler(signum, frame):
        # Raise KeyboardInterrupt - so we can handle it in the same way as Ctrl-C
        raise KeyboardInterrupt()

    # Create and run worker
    worker = None
    try:
        signal.signal(signal.SIGTERM, term_handler)
        worker = Worker(args)
        worker.run()
    except Exception as e:
        logger.error(str(e))
        logger.exception("Fatal exception!")
    except (KeyboardInterrupt):
        logger.info('SIGINT received, aborting ...')
    finally:
        if worker:
            logger.info("worker found ... calling exit")
            worker.exit()
    return 0

def main(sysargv: Optional[List[str]] = None) -> None:
    """
    This function will initiate the bot and start the trading loop.
    :return: None
    """

    return_code: Any = 1
    try:
        # setup_logging_pre()
        arguments = Arguments(sysargv)
        args = arguments.get_parsed_arg()
        
        # Call subcommand.
        if 'func' in args:
            logger.info(f'IBuzz {__version__}')
            gc_set_threshold()
            # return_code = args['func'](args)
            return_code = start_trading(args)
        else:
            # No subcommand was issued.
            # raise OperationalException(
            #     "Usage of IBuzz requires a subcommand to be specified."
            # )
            return_code = start_trading(args)

    except SystemExit as e:  # pragma: no cover
        return_code = e
    except KeyboardInterrupt:
        logger.info('SIGINT received, aborting ...')
        return_code = 0
    except FreqtradeException as e:
        logger.error(str(e))
        return_code = 2
    except Exception:
        logger.exception('Fatal exception!')
    finally:
        sys.exit(return_code)


if __name__ == '__main__':  # pragma: no cover
    main()
