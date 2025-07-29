
"""Cli support for the 'service' command."""

from argparse import ArgumentParser, Namespace
import sys
import json
from tabulate import tabulate
from ..client import WaylayClient
from ..service.util.info import DESC_LEVELS

COMMANDS = [LIST, DOC] = ['list', 'doc']


def init_srv_parser(parser: ArgumentParser):
    """Initialize parser for the service command."""
    cmd_parsers = parser.add_subparsers(dest='srv_cmd', description='Inspect service definitions.')
    cmd_list = cmd_parsers.add_parser(
        LIST, help='List services.', description='List all defined services.')
    init_doc_parser(cmd_parsers.add_parser(
        DOC,
        help='Generate an HTML SDK overview.',
        description='Generate an HTML SDK overview.'
    ))
    cmd_list.add_argument(
        '--json', dest='format_json', default=False, action="store_true",
        help='If set, list as json data.'
    )
    cmd_list.add_argument(
        '--format', dest='format', default='github',
        help='A format supported by [tabulate](https://pypi.org/project/tabulate).'
    )
    return parser


def init_doc_parser(parser: ArgumentParser):
    """Initialize parser for the doc command."""
    parser.add_argument(
        '-s', '--service', dest='doc_service', nargs='*',
        help='Filter services to document.', default=None
    )
    parser.add_argument(
        '-r', '--resource', dest='doc_resource', nargs='*',
        help='Filter resources to document.', default=None
    )
    parser.add_argument(
        '-l', '--link', dest='doc_link', nargs='*', help='Filter doc sites links.', default=None
    )
    parser.add_argument(
        '-d', '--doc_url', dest='doc_url',
        help='Set the root of the documentation site.', default='https://docs.waylay.io/#'
    )
    parser.add_argument(
        '-a', '--apidoc_url', dest='apidoc_url',
        help='Set the root of the api documentation site.', default='https://docs.waylay.io/openapi/public/redocly'
    )
    parser.add_argument(
        '--desc-level', dest='desc_lvl', nargs='*',
        help='Specify the included descriptions.',
        choices=DESC_LEVELS,
        default=None
    )
    return parser


def handle_srv_cmd(waylay: WaylayClient, args: Namespace) -> bool:
    """Execute a service command."""
    if args.srv_cmd is None:
        handle_srv_list_cmd(waylay, Namespace(format_json=False, profile=None, format='github'))
        return True
    if args.srv_cmd == LIST:
        handle_srv_list_cmd(waylay, args)
        return True
    if args.srv_cmd == DOC:
        handle_doc_cmd(waylay, args)
        return True

    return False


def handle_doc_cmd(client: WaylayClient, args: Namespace) -> bool:
    """Execute documentation generation."""
    client.config.set_local_settings(doc_url=args.doc_url, apidoc_url=args.apidoc_url)
    print(client.util.info.action_info_html(
        service=args.doc_service, resource=args.doc_resource, links=args.doc_link, desc_levels=args.desc_lvl
    ))
    return True


def handle_srv_list_cmd(waylay: WaylayClient, args: Namespace):
    """Execute the service list command."""
    if args.format_json:
        json.dump([
            {
                'key': srv.service_key,
                'root_url': srv.get_root_url(),
                'description': srv.description,
                'resources': [
                    r.as_dict()
                    for r in srv.resources
                ]
            }
            for srv in waylay.services
        ], sys.stdout)
        return
    profile = f'profile "{args.profile}"' if args.profile else 'default profile'
    header = [
        "key", f" url for {profile}", "description"
    ]
    table = [
        [srv.service_key, srv.get_root_url() or '', srv.description]
        for srv in waylay.services
    ]
    print(tabulate(table, headers=header, tablefmt=args.format))
