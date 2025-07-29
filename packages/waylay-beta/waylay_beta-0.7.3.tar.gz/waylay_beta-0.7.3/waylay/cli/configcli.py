"""Cli support for the 'doc' command."""

from argparse import Namespace, ArgumentParser
from tabulate import tabulate
import json

from ..exceptions import ConfigError

from ..auth_interactive import ask_yes_no

from ..config import WaylayConfig, DEFAULT_PROFILE
from ..client import WaylayClient

COMMANDS = [LIST, SHOW, CREATE, REMOVE, DEFAULT, TOKEN] = ['list', 'show', 'create', 'remove', 'default', 'token']
DEFAULT_COMMAND = LIST


def init_parser(parser: ArgumentParser):
    """Initialize parser for the config command."""
    cmd_parsers = parser.add_subparsers(
        dest='config_cmd',
        description='Manage configuration profiles.'
    )
    cmd_parsers.add_parser(
        LIST,
        help='List config profiles.',
        description='List config profiles.'
    )
    show_cmd = cmd_parsers.add_parser(
        SHOW,
        help='Show an existing config profile.',
        description='Show an existing config profile.'
    )
    show_cmd.add_argument(
        'profiles', nargs='*',
        help='Specify one or more profile names. Defaults to the current profile.',
    )
    create_cmd = cmd_parsers.add_parser(
        CREATE,
        help='Create a new profile',
        description='Create a new profile'
    )
    create_cmd.add_argument(
        'new_profile', nargs='?',
        help='Specify a new profile name. Defaults to the current profile.'
    )
    remove_cmd = cmd_parsers.add_parser(
        REMOVE,
        help='Remove config profile.',
        description='Remove config profile.',
    )
    remove_cmd.add_argument(
        'profiles', nargs='+',
        help='Specify one or more profile names.'
    )
    default_cmd = cmd_parsers.add_parser(
        DEFAULT,
        help='Make a profile default.',
        description='Make a profile default.',
    )
    default_cmd.add_argument(
        'from_profile', nargs='?',
        help='Specify the profile you want to copy as default.'
    )
    token_cmd = cmd_parsers.add_parser(
        TOKEN,
        help='Fetch a token for the active profile.',
        description='Fetch a token for the active profile.',
    )
    token_cmd.add_argument(
        '--decode', dest='token_decode', default=False, action="store_true",
        help='Show the decode token data.'
    )
    return parser


def handle_config_list_cmd(args: Namespace):
    """Execute the config list command."""
    header = [
        "profile", "current", "credential", "id", "cluster"
    ]
    current_profile = args.profile or DEFAULT_PROFILE
    table = [
        [
            profile,
            '*' if profile == current_profile else '',
            config.credentials.credentials_type if config else '*invalid*',
            config.credentials.id if config else '*invalid*',
            config.gateway_url or config.accounts_url if config else '*invalid*'
        ]
        for profile in WaylayConfig.list_profiles()
        for config in [WaylayConfig.load(profile, interactive=False, skip_error=True)]
    ]
    print(tabulate(table, headers=header, tablefmt='github'))


def handle_config_show_cmd(args: Namespace):
    """Execute the config show command."""
    current_profile = args.profile or DEFAULT_PROFILE
    profiles = args.profiles or [current_profile]
    for profile in profiles:
        try:
            config = WaylayConfig.load(profile, interactive=False)
        except ConfigError as exc:
            print(f'ERR: {exc}')
        else:
            print(config.config_file_path(profile))
            print(json.dumps(config.to_dict(obfuscate=True), indent=2))


def handle_config_create_cmd(args: Namespace):
    """Execute the config show command."""
    profile = args.new_profile or args.profile or DEFAULT_PROFILE
    print(f"Creating configuration profile '{profile}'.")
    if profile in WaylayConfig.list_profiles():
        print(f"ERR: profile '{profile}' already exists.")
        return
    try:
        config = WaylayConfig.load(profile, interactive=True)
    except ConfigError as exc:
        print(f'ERR: {exc}')
    else:
        print(config.config_file_path(profile))
        print(json.dumps(config.to_dict(obfuscate=True), indent=2))


def handle_config_remove_cmd(args: Namespace):
    """Execute the config remove command."""
    profile_matchers = args.profiles
    to_remove = [
        profile for profile in WaylayConfig.list_profiles()
        if profile in profile_matchers
    ]
    if not to_remove:
        print('No matching profiles found.')
    for remove_profile in to_remove:
        if ask_yes_no(f"Removing profile '{remove_profile}'? (y/n): ", True):
            WaylayConfig.delete(remove_profile)
            print(f"Removed '{remove_profile}'")
        else:
            print(f"Skipped '{remove_profile}'")


def handle_config_default_cmd(args: Namespace):
    """Execute the config default command."""
    profile = args.from_profile or args.profile or DEFAULT_PROFILE
    if (profile == DEFAULT_PROFILE):
        print('Already default profile.')
        return
    config = WaylayConfig.load(profile)
    config.profile = DEFAULT_PROFILE
    config.save()
    print(f"Copied and saved profile '{profile}' as default to '{config.config_file_path()}'")


def handle_config_token_cmd(args: Namespace):
    """Execute the config default command."""
    profile = args.profile or DEFAULT_PROFILE
    token = WaylayConfig.load(profile).get_valid_token()
    if args.token_decode:
        print(json.dumps(token.token_data, indent=4))
    else:
        print(token.token_string)


COMMAND_HANDLERS = {
    LIST: handle_config_list_cmd,
    SHOW: handle_config_show_cmd,
    CREATE: handle_config_create_cmd,
    REMOVE: handle_config_remove_cmd,
    DEFAULT: handle_config_default_cmd,
    TOKEN: handle_config_token_cmd
}


def handle_cmd(client: WaylayClient, args: Namespace) -> bool:
    """Handle config cmd."""
    cmd = args.config_cmd or DEFAULT_COMMAND
    handler = COMMAND_HANDLERS.get(cmd)
    if handler:
        handler(args)
        return True
    return False
