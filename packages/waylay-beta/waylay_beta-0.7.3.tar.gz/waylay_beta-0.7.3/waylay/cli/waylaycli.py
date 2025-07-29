"""Command line interface for the Waylay Python SDK."""

import argparse
import logging

from waylay import WaylayClient

from . import seriescli, servicecli, configcli


CLI_COMMANDS = [CMD_SERVICE, CMD_SERIES, CMD_CONFIG] = ['service', 'series', 'config']


def main():
    """Start the waylaycli program."""
    logging.basicConfig()
    parser = argparse.ArgumentParser(
        prog='waylaycli', description='Command line interface to the Waylay Python SDK',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '-p', '--profile', dest='profile', nargs='?', help='Configuration profile.', default=None
    )
    parser.add_argument(
        '-l', '--loglevel', dest='log_level', nargs='?',
        default='WARNING', type=lambda _: _.upper(),
        help=f"Log level for waylay packages. One of {','.join(logging._levelToName.values())}.",

    )
    parser.add_argument(
        '--libloglevel', dest='lib_log_level', nargs='?',
        default='WARNING', type=lambda _: _.upper(),
        help=f"Log level for other packages. One of {','.join(logging._levelToName.values())}.",
    )
    cmd_parsers = parser.add_subparsers(dest='cmd')
    servicecli.init_srv_parser(
        cmd_parsers.add_parser(CMD_SERVICE, help='List available services.'))
    seriescli.init_series_parser(
        cmd_parsers.add_parser(CMD_SERIES, help='Interact with waylay timeseries.'))
    configcli.init_parser(
        cmd_parsers.add_parser(CMD_CONFIG, help='Manage Waylay client configuration profiles.'))
    args = parser.parse_args()

    def waylay_client():
        return WaylayClient.from_profile(args.profile)

    waylay_logger = logging.getLogger('waylay')
    try:
        import coloredlogs
        coloredlogs.install(level='DEBUG')
    except ImportError:
        pass
    logging.getLogger().setLevel(args.lib_log_level)
    waylay_logger.setLevel(args.log_level)
    done = False
    if args.cmd == CMD_SERVICE:
        done = servicecli.handle_srv_cmd(waylay_client(), args)
    if args.cmd == CMD_SERIES:
        done = seriescli.handle_series_cmd(waylay_client(), args)
    if args.cmd == CMD_CONFIG:
        done = configcli.handle_cmd(None, args)
    if not done:
        parser.print_help()
