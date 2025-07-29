"""Python SDK Documentation tooling."""

from typing import Optional, Dict, Union, List, Any, cast

import pandas as pd
import numpy as np

from waylay.service import WaylayResource, WaylayServiceContext, WaylayAction

DESC_LEVELS = [
    DESC_DESC,
    DESC_ARGS,
    DESC_RETURN,
    DESC_REST,
    DESC_WRAPPED,
    DESC_LINK,
    DESC_SDK_ACTION
] = [
    'title',
    'arguments',
    'return',
    'rest',
    'wrapped',
    'link',
    'sdk'
]


def format_links_html(links: Optional[Dict[str, Dict[str, str]]]) -> str:
    """Format link information to an html string."""
    if not links:
        return ''
    link_items = (
        f'<a href="{href}" target="{target}">{text}</a>'
        for target, href, text in (
            (f"_{key}", link.get('href'), link.get('title', key))
            for key, link in links.items()
        )
        if href
    )
    if not link_items:
        return ''
    return " | ".join(link_items)


class InfoTool(WaylayResource):
    """Client tool that exposes information about the provided services, recources and operations."""

    _service_context: WaylayServiceContext

    actions: Dict[str, Any] = {
        'action_info_df': {'wrapped_actions': []},
        'action_info_html': {'wrapped_actions': []}
    }

    def set_context(self, service_context):
        """Configure this tool with a service context."""
        self._service_context = service_context

    def action_info_df(
        self,
        service: Optional[Union[str, List[str]]] = None,
        resource: Optional[Union[str, List[str]]] = None,
        links: Optional[Union[str, List[str]]] = None,
        desc_levels: Optional[Union[str, List[str]]] = None,
        include_private: bool = False
    ) -> pd.DataFrame:
        """Produce a pandas DataFrame with an overview of the provided actions.

Arguments:
    service     filter on the services to be listed
    resource    filter on the resources to be listed
    links       filter on the documentation link names
        """

        def service_filter(name):
            return service is None or name == service or name in service

        def resource_filter(name):
            return resource is None or name == resource or name in resource

        def format_filtered_links(doc_links):
            if not doc_links:
                return ''
            return format_links_html(
                {
                    link: ref
                    for link, ref in doc_links.items()
                    if not links or link in links
                }
            )

        def format_pydoc(docstr: Optional[str]) -> Optional[str]:
            if not docstr:
                return docstr
            return f'<pre>{docstr.strip()}\n</pre>'

        def format_rest_action(docstr: Optional[str]) -> Optional[str]:
            if not docstr:
                return docstr
            return f'<b><pre>{docstr.strip()}\n</pre></b>'

        lvls = desc_levels or DESC_LEVELS

        def action_doc(action: WaylayAction) -> str:
            return "\n".join(f'<div>{doc}</div>' for doc in [
                action.description if DESC_DESC in lvls else None,
                format_pydoc(action.arguments_doc) if DESC_ARGS in lvls else None,
                format_pydoc(action.returns_doc) if DESC_RETURN in lvls else None,
                format_pydoc(action.sdk_action_doc) if DESC_SDK_ACTION in lvls else None,
                *([
                    wrapped_doc
                    for wrapped_action in cast(WaylayAction, getattr(action, 'wrapped_actions', []))
                    for wrapped_doc in [
                        'Can use the following REST action:',
                        format_rest_action(wrapped_action.rest_action_doc) if DESC_REST in lvls else None,
                        wrapped_action.description if DESC_DESC in lvls else None,
                        format_pydoc(wrapped_action.arguments_doc) if DESC_ARGS in lvls else None,
                        format_pydoc(wrapped_action.returns_doc) if DESC_RETURN in lvls else None,
                        format_pydoc(wrapped_action.sdk_action_doc) if DESC_SDK_ACTION in lvls else None,
                    ]
                ] if DESC_WRAPPED in lvls else []),
                format_rest_action(action.rest_action_doc) if DESC_REST in lvls else None,
                format_filtered_links(action.doc_links) if DESC_LINK in lvls else None,
            ] if doc)

        df_doc = pd.DataFrame(np.transpose([
            [
                service.service_key,
                resource.resource_name,
                action.name,
                action_doc(action),
            ]
            for service in self._service_context.list()
            if service_filter(service.name)
            for resource in service.resources
            if resource_filter(resource.name)
            for action_id, action in resource.actions.items()
            if include_private or not action.name.startswith('_')
        ]), index=[
            'service',
            'resource',
            'action',
            'description'
        ], ).T
        return df_doc.set_index(['service', 'resource', 'action'])

    def action_info_html(
        self,
        service: Optional[Union[str, List[str]]] = None,
        resource: Optional[Union[str, List[str]]] = None,
        links: Optional[Union[str, List[str]]] = None,
        desc_levels: Optional[Union[str, List[str]]] = None
    ) -> str:
        """Render the service/resource/action listing as an html table.

Arguments:
    service     filter on the services to be listed
    resource    filter on the resources to be listed
    links       filter on the documentation link names
        """
        html = self.action_info_df(service, resource, links, desc_levels).to_html(
            escape=False,
            header=False,
            index_names=False,
        )
        # custom header
        html = html.replace('<tbody>', """<thead>
  <tr>
    <th>service</th>
    <th>resource</th>
    <th>action</th>
    <th>description</th>
  </tr>
</thead>
<tbody>""")
        # replace double escapes in html
        return html.replace('\\n', "\n")
