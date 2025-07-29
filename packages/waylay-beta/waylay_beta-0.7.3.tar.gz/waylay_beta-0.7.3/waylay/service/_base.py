"""Base classes for Waylay REST Services and Resources."""
__docformat__ = "google"

from typing import (
    Optional, Type, TypeVar,
    Mapping, List, Dict, Optional,
    Callable, Collection, Any, Union,
    cast
)
try:
    from typing import Protocol
except ImportError:
    # typing.Protocol is a 3.8 feature ...
    # ... but typing_extensions provides forward compatibility.
    from typing_extensions import Protocol  # type: ignore

from string import Template

from simple_rest_client.api import Resource, API
from waylay.config import WaylayConfig
from waylay.exceptions import ConfigError

S = TypeVar('S', bound='WaylayService')
RS = TypeVar('RS', bound='WaylayRESTService')
R = TypeVar('R', bound='WaylayResource')


class WaylayServiceContext(Protocol):
    """View protocol for the dynamic service context."""

    def get(self, service_class: Type[S]) -> Optional[S]:
        """Get the service instance for the given class, if available."""

    def require(self, service_class: Type[S]) -> S:
        """Get the service instances for the given class or raise a ConfigError."""

    def list(self) -> List['WaylayService']:
        """List all available service instances."""


DEFAULT_SERVICE_TIMEOUT = 10


def _arg_doc(arg):
    desc = f"    {arg['name']} ({arg['type']}): {arg['description']}"
    if 'examples' not in arg:
        return desc
    examples = '\n'.join(
        f'        - {ex}' for ex in arg['examples']
    )
    return (
        desc +
        f'\n       Examples:\n{examples}'
    )

# Implementation Note
# -------------------
# Current solution is scaffolded around the `simple_rest_client`, but is planned to be refactored.


class WaylayAction(dict):
    """Configuration object for a service action."""

    @property
    def resource(self) -> 'WaylayResource':
        """Get the parent resource of this action."""
        return self['_resource']

    @property
    def id(self) -> str:
        """Get the action id."""
        return self['id']

    @property
    def name(self) -> str:
        """Get the action name as exposed in the SDK."""
        return self.get('name', self.id)

    @property
    def description(self) -> Optional[str]:
        """Get the action description."""
        desc = self.get('description')
        if desc:
            return desc
        return (self.action_method.__doc__ or '').split("\n")[0]

    @property
    def arguments(self) -> List[Dict]:
        """Get the arguments documentation info."""
        return self.get('arguments', [])

    @property
    def returns(self) -> List[Dict]:
        """Get the returns documentation info."""
        return self.get('returns', [])

    @property
    def doc_links(self) -> Dict[str, Dict[str, str]]:
        """Get (documentation) links templates."""
        roots = self.resource.hal_roots
        return {
            link: dict(href=roots.get(link, '') + ref)
            for link, ref in self.get('links', {}).items()
        }

    @property
    def rest_action_doc(self) -> str:
        """Get the documentation string for the REST action."""
        return ''

    @property
    def action_method(self) -> Callable:
        """Get the SDK action method that is used to expose this action."""
        return getattr(self.resource, self.id)

    @property
    def sdk_action_method(self) -> Callable:
        """Get the REST action method that is used to expose this action."""
        return getattr(self.resource, self.name)

    @property
    def sdk_action_doc(self) -> str:
        """Get the sdk python documentation for this action."""
        doc = self.sdk_action_method.__doc__ or ''
        if self.description and doc.startswith(self.description):
            doc = doc[len(self.description):]
        if self.name != self.id:
            # wrapped actions
            doc += "\n" + (self.action_method.__doc__ or '')
        return doc

    @property
    def arguments_doc(self) -> str:
        """Get the argument documentation for this action."""
        args = self.arguments
        if not args:
            return ''
        return '  Arguments:\n' + '\n'.join(
            _arg_doc(arg)
            for arg in args
        )

    @property
    def returns_doc(self) -> str:
        """Get the return value documentation for this action."""
        returns = self.returns
        if not returns:
            return ''
        return '  Returns: \n' + '\n'.join(
            _arg_doc(ret)
            for ret in returns
        )

    def __repr__(self):
        """Get a string representation of this action."""
        return self.name

    def as_dict(self):
        """Get a dictionary representation."""
        return {
            'name': self.name,
            'description': self.description
        }

    @property
    def fqn(self):
        """Get the fully qualified name for this action."""
        return f'{self.resource.fqn}.{self.name}'


class WaylayRESTAction(WaylayAction):
    """Configuration object representing a single Waylay REST action."""

    @property
    def method(self) -> Optional[str]:
        """Get the action HTTP method."""
        return self.get('method')

    @property
    def url(self) -> Optional[str]:
        """Get the action url template."""
        return self.get('url')

    def __repr__(self):
        """Get a string representation of this REST action."""
        return f"{self.method} {self.url}"

    @property
    def rest_action_doc(self) -> str:
        """Get the documentation string for the REST action."""
        url_interpolated = self.url
        if self.arguments and self.url:
            url_interpolated = self.url.format(*[f"{{{arg['name']}}}" for arg in self.arguments])
        return f'{self.method} {self.resource.service.gateway_root_path}{url_interpolated}'

    def as_dict(self):
        """Get a dictionary representation."""
        return {
            'name': self.name,
            'description': self.description,
            'rest': self.rest_action_doc
        }


class WaylayRESTActionsWrapper(WaylayAction):
    """Configuration object representing a method that wraps one or more REST actions."""

    @property
    def wrapped_actions(self) -> List[WaylayRESTAction]:
        """Get the list of wrapped REST actions as defined by 'wrapped_actions'."""
        return [
            cast(WaylayRESTAction, self.resource.actions[id])
            for id in self.get('wrapped_actions', [])
        ]

    @property
    def doc_links(self) -> Dict[str, Dict[str, str]]:
        """Get (documentation) links templates."""
        roots = self.resource.hal_roots
        return {
            link: dict(href=roots.get(link, '') + ref)
            for wrapped_action in self.wrapped_actions
            for link, ref in wrapped_action.get('links', {}).items()
        }


def create_waylay_action(**kwargs) -> WaylayAction:
    """Initialize a waylay action that wraps a REST call or other method."""
    if 'url' in kwargs:
        return WaylayRESTAction(**kwargs)
    if 'wrapped_actions' in kwargs:
        return WaylayRESTActionsWrapper(**kwargs)
    raise ValueError("A waylay action configuration requires either an 'url' or 'wrapped_actions'.")


class WaylayResource(Resource):
    """Client object representing a Waylay REST Resource.

    This is a collection of REST operations that have a single Waylay Entity as subject.
    """

    service: 'WaylayService'
    resource_name: str
    actions: Dict[str, Union[WaylayAction, Collection[Any]]]

    # class variables
    link_roots: Dict[str, str] = {}

    def __init__(self, *args, **kwargs):
        """Create a Waylay Resource."""
        self.service = kwargs.pop('service', None)
        self.actions = {
            id: create_waylay_action(id=id, _resource=self, **action)
            for id, action in self.actions.items()
        }
        super().__init__(*args, **kwargs)

    @property
    def name(self):
        """Get the name that identifies this resource in the Python SDK."""
        return self.resource_name

    @property
    def description(self):
        """Get a description of this service."""
        return self.__doc__

    def add_action(self, action_name: str):
        """Add action, and apply decorators."""
        if isinstance(self.actions[action_name], WaylayRESTAction):
            super().add_action(action_name)
        self.decorate_action(action_name)

    def decorate_action(self, action_name):
        """Decorate the action if a 'decorators' definition exist."""
        action = self.get_action(action_name)
        decorators = action.get('decorators', None)
        action_method = getattr(self, action_name)
        action_method.__dict__['action'] = action
        if decorators:
            for decorator in decorators:
                action_method = decorator(action_method)
                action_method.__dict__['action'] = action
        setattr(self, action_name, action_method)

    def __repr__(self):
        """Get a technical string representation of this action."""
        actions_repr = ', '.join(
            f"{name}: {action_def}"
            for name, action_def in self.actions.items()
        )
        return (
            f"<{self.__class__.__name__}("
            f"actions=[{actions_repr}]"
            ")>"
        )

    def as_dict(self):
        """Get a dictionary representation."""
        return {
            'name': self.resource_name,
            'description': self.description,
            'actions': [
                a.as_dict()
                for a in self.actions.values()
            ],
            '_links': self.doc_links(None)
        }

    @property
    def hal_roots(self) -> Dict[str, str]:
        """Get the root urls for documentation links if this resource."""
        return {
            link: Template(
                href_root
            ).safe_substitute(
                root_url=self.api_root_url,
                doc_url=self.service.config.doc_url,
                apidoc_url=self.service.config.apidoc_url,
            )
            for link, href_root in self.link_roots.items()
        }

    def doc_links(self, action: Optional[str]) -> Dict[str, Dict[str, str]]:
        """Create a HAL `_links` representation for (documentation) links.

        Arguments:
            action      if specified, give links for a specific action rather than the resource.
        """
        hrefs = {rel: '' for rel in self.link_roots}
        if action:
            hrefs = cast(WaylayAction, self.actions[action])['links']

        return {
            link_rel: dict(
                href=Template(
                    href_root + hrefs.get(link_rel, '')
                ).safe_substitute(
                    root_url=self.api_root_url,
                    doc_url=self.service.config.doc_url,
                    apidoc_url=self.service.config.apidoc_url,
                )
            )
            for link_rel, href_root in self.link_roots.items()
            if link_rel in hrefs
        }

    # override
    def get_action_full_url(self, action_name, *parts):
        """Override the regular url computation when not using api gateway."""
        if (self.api_root_url is None):
            srv = self.service
            raise ConfigError(
                f'The service `{srv.service_key}` has no url configuration. '
                f'Please provide a endpoint using a setting with key `{srv.config_key}`,'
                'or request your tenant administrator '
                f'to configure the global setting `waylay_{srv.config_key}`.'
            )
        return super().get_action_full_url(action_name, *parts)

    @property
    def fqn(self):
        """Get the fully qualified name for this resource."""
        return f"{self.service.fqn if self.service else '_'}.{self.name}"


class WaylayService():
    """Client object representing a Waylay Tool."""

    resource_definitions: Mapping[str, Type[Resource]]
    config: WaylayConfig
    service_key: str = ''
    plugin_priority = 0
    gateway_root_path: Optional[str] = None
    _resources: Dict[str, WaylayResource]

    def __init__(self, *args, **kwargs):
        """Create a WaylayRESTService."""
        self._resources = getattr(self, '_resources', {})
        for name, resource_class in self.resource_definitions.items():
            self._add_waylay_resource(resource_name=name, resource_class=resource_class)

    @property
    def name(self):
        """Get the name that identifies this service in the Python SDK."""
        return self.service_key

    @property
    def description(self):
        """Get a description of this service."""
        return self.__doc__

    @property
    def root_url(self) -> Optional[str]:
        """Get the root url."""
        return self.get_root_url()

    @property
    def resources(self):
        """Get the resources supported by this service."""
        return self.list_resources()

    def _add_waylay_resource(self, resource_name: str, resource_class: Type[R], **kwargs) -> R:
        waylay_resource = resource_class(service=self)
        setattr(self, resource_name, waylay_resource)
        self._resources[resource_name] = waylay_resource
        waylay_resource.resource_name = resource_name
        waylay_resource.service = self
        return waylay_resource

    def list_resources(self) -> List[WaylayResource]:
        """List the WaylayResources of this service."""
        return list(self._resources.values())

    def configure(self: S, config: WaylayConfig, context: WaylayServiceContext) -> S:
        """Configure endpoints and authentication with given configuration.

        Returns self
        """
        self.config = config
        return self.reconfigure()

    def reconfigure(self: S) -> S:
        """Configure endpoints and authentication with current configuration.

        Returns self
        """
        return self

    def get_root_url(self) -> Optional[str]:
        """Get the root url."""
        return None

    def __repr__(self):
        """Get a technical string representation of this tool."""
        return (
            f"<{self.__class__.__name__}("
            f"service_key={self.service_key},"
            ")>"
        )

    @property
    def fqn(self):
        """Get the fully qualified name for this service."""
        return f'waylay:{self.service_key}'


class WaylayRESTService(API, WaylayService):
    """Client object representing a Waylay Service.

    A collection of Resources with their operations.
    """

    # class variables
    config_key: str = 'api'
    default_root_path: str = ''
    link_templates: Dict[str, str] = {}

    def __init__(self, *args, **kwargs):
        """Create a WaylayRESTService."""
        timeout = kwargs.pop('timeout', DEFAULT_SERVICE_TIMEOUT)
        json_encode_body = kwargs.pop('json_encode_body', True)
        API.__init__(self, *args, timeout=timeout, json_encode_body=json_encode_body, **kwargs)
        WaylayService.__init__(self, *args, **kwargs)

    def _add_waylay_resource(self, resource_name: str, resource_class: Type[R], **kwargs) -> R:
        self.add_resource(resource_name=resource_name, resource_class=resource_class, **kwargs)
        waylay_resource: R = self._resources[self.correct_attribute_name(resource_name)]
        waylay_resource.service = self
        return waylay_resource

    def set_root_url(self, root_url):
        """Set the root url and reconfigure the service."""
        self.config.set_root_url(self.config_key, root_url)
        self.reconfigure()

    def get_root_url(self) -> Optional[str]:
        """Get the root url."""
        if self.config is None:
            return None
        return self.config.get_root_url(
            self.config_key,
            gateway_root_path=self.gateway_root_path,
            default_root_path=self.default_root_path
        )

    def reconfigure(self: RS) -> RS:
        """Configure endpoints and authentication with current configuration.

        Returns self
        """
        if self.config is None:
            return self
        root_url = self.get_root_url()
        for resource in self._resources.values():
            resource.api_root_url = root_url
            resource.client.auth = self.config.auth
        return self

    def __repr__(self):
        """Get a technical string representation of this service."""
        return (
            f"<{self.__class__.__name__}("
            f"service_key={self.service_key},"
            f"config_key={self.config_key},"
            f"root_url={self.get_root_url()},"
            f"resources=[{', '.join(self._resources.keys())}]"
            ")>"
        )

    def doc_links(self) -> Dict[str, Dict[str, str]]:
        """Create a HAL `_links` representation for the documentation links."""
        return {
            rel: dict(href=Template(href).safe_substitute(
                root_url=self.root_url,
                doc_url=self.config.doc_url,
                apidoc_url=self.config.apidoc_url,
            ))
            for rel, href in self.link_templates.items()
        }
