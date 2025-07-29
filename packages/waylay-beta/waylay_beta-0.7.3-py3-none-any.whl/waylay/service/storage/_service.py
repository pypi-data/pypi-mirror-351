"""REST client for the Waylay Storage Service."""

from waylay.service import WaylayRESTService

from .bucket import BucketResource
from .object import ObjectResource, FolderResource
from .content import ContentTool
from .about import AboutResource
from .subscription import SubscriptionResource


class StorageService(WaylayRESTService):
    """REST client for the Waylay Storage Service."""

    config_key = 'storage'
    service_key = 'storage'
    gateway_root_path = '/storage/v1'

    resource_definitions = {
        'bucket': BucketResource,
        'object': ObjectResource,
        'folder': FolderResource,
        'subscription': SubscriptionResource,
        'about': AboutResource,
        'content': ContentTool,
    }

    bucket: BucketResource
    object: ObjectResource
    folder: FolderResource
    subscription: SubscriptionResource
    about: AboutResource
    content: ContentTool
