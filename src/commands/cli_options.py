"""
Definition of cli arguments used in arguments.py
"""
from argparse import SUPPRESS, ArgumentTypeError

from src import __version__, constants

class Arg:
    # Optional CLI arguments
    def __init__(self, *args, **kwargs):
        self.cli = args
        self.kwargs = kwargs


# List of available command line options
AVAILABLE_CLI_OPTIONS = {
    # Common options
    "verbosity": Arg(
        '-v', '--verbose',
        help='Verbose mode (-vv for more, -vvv to get all messages).',
        action='count',
        default=0,
    ),
    "logfile": Arg(
        '--logfile', '--log-file',
        help="Log to the file specified. Special values are: 'syslog', 'journald'. "
             "See the documentation for more details.",
        metavar='FILE',
    ),
    "version": Arg(
        '-V', '--version',
        action='version',
        version=f'%(prog)s {__version__}',
    ),
    "config": Arg(
        '-c', '--config',
        help=f'Specify configuration file (default: `userdir/{constants.DEFAULT_CONFIG}` '
        f'or `config.json` whichever exists). '
        f'Multiple --config options may be used. '
        f'Can be set to `-` to read config from stdin.',
        action='append',
        metavar='PATH',
    ),
}
