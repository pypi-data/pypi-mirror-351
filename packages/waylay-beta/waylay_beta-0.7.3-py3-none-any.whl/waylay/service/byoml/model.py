"""REST definitions for the 'model' entity of the 'byoml' service."""

from contextlib import contextmanager

from functools import wraps
from typing import (
    Callable, List, Any, Union, Dict, Optional
)
import json
import pandas as pd
import logging

from waylay.service import WaylayRESTService
from .._base import WaylayResource
from .._decorators import (
    return_body_decorator,
    return_path_decorator,
    default_timeout_decorator,
    suppress_header_decorator,
    log_server_timing_decorator,
)
from ._decorators import (
    byoml_exception_decorator,
    byoml_retry_decorator,
    byoml_raise_not_ready_get,
    byoml_retry_upload_after_deletion_decorator,
    DEFAULT_BYOML_MODEL_TIMEOUT
)
from ...exceptions import (
    RestRequestError,
)
from ._model_archive import (
    ModelPlugArchiveBuilder,
    ModelZipArchiveBuilder,
    ByomlModel, PathLike
)

LOG = logging.getLogger(__name__)

DEFAULT_MODEL_UPLOAD_TIMEOUT = 120

LOG_SERVER_TIMING = logging.getLogger(__name__ + '.server-timing')
byoml_server_timing_decorator = log_server_timing_decorator(LOG_SERVER_TIMING, logging.INFO)

MODEL_NAME_ARG = {
    'name': 'model_name',
    'type': 'str',
    'description': 'name for the model',
    'example': 'my_prediction_model_001'
}
MODEL_RESULT = {
    'name': 'model',
    'type': 'Dict',
    'description': 'A representation of the model deployment.'
}
MODEL_INFERENCE_RESULT = {
    'name': 'results',
    'type': 'List',
    'description': 'The results of a model inference, normally a list of list of numerical data.'
}


def _input_data_as_list(input_data):
    if isinstance(input_data, list):
        if not input_data:
            # empty list
            return input_data

        if hasattr(input_data[0], 'tolist'):
            # list of numpy arrays
            return [d.tolist() for d in input_data]

        if isinstance(input_data[0], (pd.DataFrame, pd.Series)):
            # list of pandas
            return [d.values.tolist() for d in input_data]

        # list of (list of ...) value types?
        return input_data

    # pandas
    if isinstance(input_data, (pd.DataFrame, pd.Series)):
        return input_data.values.tolist()

    # numpy arrays
    if hasattr(input_data, 'tolist'):
        return input_data.tolist()

    raise RestRequestError(
        f'input data of unsupported type {type(input_data)}'
    )


def model_execution_request_decorator(action_method):
    """Decorate an action to prepare the execution of the model.

    Transforms any input data into a list, and provides it
    as `instances` in the request body.
    """
    @wraps(action_method)
    def wrapped(model_name, input_data=None, **kwargs):
        body = kwargs.pop('body', {})
        if 'instances' not in body:
            body = {
                'instances': _input_data_as_list(input_data),
                **body
            }
        return action_method(
            model_name,
            body=body,
            **kwargs
        )
    return wrapped


def _execute_model_decorators(response_key: str) -> List[Callable]:
    return [
        byoml_server_timing_decorator,
        byoml_exception_decorator,
        byoml_retry_decorator,
        model_execution_request_decorator,
        return_path_decorator(
            [response_key],
            default_response_constructor=None,
            response_constructor_advice="Use 'np.array' to return a numpy array, 'pd.DataFrame' for a pandas dataframe."
        )
    ]


class ModelResource(WaylayResource):
    """REST Resource for the 'model' entity of the 'byoml' service."""

    service: WaylayRESTService

    link_roots = {
        'doc': '${doc_url}/api/byoml/?id=',
        'apidoc': '${apidoc_url}/byoml.html'
    }

    actions = {
        'list': {
            'method': 'GET',
            'url': '/models',
            'returns': [
                {
                    'name': 'models',
                    'type': 'List[Dict]',
                    'description': 'A list of metadata objects for available models'
                }
            ],
            'decorators': [
                byoml_server_timing_decorator,
                byoml_exception_decorator,
                return_path_decorator(['available_models'])
            ],
            'description': 'List the metadata of the deployed <em>BYOML Models</em>',
            'links': {
                'doc': 'overview-of-the-api',
                'apidoc': '',
            },
        },
        'list_names': {
            'method': 'GET',
            'url': '/models',
            'decorators': [
                byoml_server_timing_decorator,
                byoml_exception_decorator,
                return_path_decorator(['available_models', 'name'])
            ],
            'returns': [
                {
                    'name': 'model_names',
                    'type': 'List[str]',
                    'description': 'A list of names of deployed models.'
                }
            ],
            'description': 'List the names of deployed <em>BYOML Models</em>',
            'links': {
                'doc': 'overview-of-the-api',
                'apidoc': '',
            },
        },
        '_create': {
            'method': 'POST',
            'url': '/models',
            'decorators': [
                byoml_server_timing_decorator,
                byoml_exception_decorator,
                default_timeout_decorator(DEFAULT_MODEL_UPLOAD_TIMEOUT),
                byoml_retry_upload_after_deletion_decorator,
                return_body_decorator,
            ],
            'description': (
                'Build and create a new <em>BYOML Model</em> as specified in the request'
            ),
            'links': {
                'doc': 'how-to-upload-your-model',
                'apidoc': '',
            },
        },
        'upload': {
            'wrapped_actions': ['_create']
        },
        '_replace': {
            'method': 'PUT',
            'url': '/models/{}',
            'arguments': [MODEL_NAME_ARG],
            'decorators': [
                byoml_server_timing_decorator,
                byoml_exception_decorator,
                default_timeout_decorator(DEFAULT_MODEL_UPLOAD_TIMEOUT),
                return_body_decorator,
            ],
            'description': 'Build and replace the named <em>BYOML Model</em>',
            'links': {
                'doc': 'overwriting-a-model',
                'apidoc': '',
            },
        },
        'replace': {
            'wrapped_actions': ['_replace']
        },
        'get': {
            'method': 'GET',
            'url': '/models/{}',
            'arguments': [MODEL_NAME_ARG],
            'returns': [MODEL_RESULT],
            'decorators': [
                byoml_server_timing_decorator,
                byoml_exception_decorator,
                byoml_raise_not_ready_get,
                byoml_retry_decorator,
                return_body_decorator,
            ],
            'description': 'Fetch the metadata of the named <em>BYOML Model</em>',
            'links': {
                'doc': 'checking-out-your-model',
                'apidoc': '',
            },
        },
        'update': {
            'method': 'PATCH',
            'url': '/models/{}',
            'arguments': [
                MODEL_NAME_ARG,
                {
                    'name': 'body',
                    'type': 'Dict[str,str]',
                    'description': 'metadata attributes for the model',
                    'examples': ['{"description":"Updated"}']
                }
            ],
            'returns': [MODEL_RESULT],
            'decorators': [
                byoml_server_timing_decorator,
                byoml_exception_decorator,
                byoml_retry_decorator,
                return_body_decorator,
            ],
            'description': (
                'Update the metadata of the named <em>BYOML Model</em>.\n'
                'Only metadata attributes can be modified.'
            ),
            'links': {
                'doc': 'update-metadata-for-a-model',
                'apidoc': '',
            },
        },
        # ## not yet supported on plug-registry
        # 'get_content': {
        #     'method': 'GET',
        #     'url': '/models/{}/content',
        #     'arguments': [
        #         MODEL_NAME_ARG
        #     ],
        #     'decorators': [
        #         byoml_server_timing_decorator,
        #         byoml_exception_decorator
        #     ],
        #     'description': 'Fetch the content of the named <em>BYOML Model</em>',
        #     'links': {
        #         'doc': 'checking-out-your-model'
        #     },
        # },
        'examples': {
            'method': 'GET',
            'url': '/models/{}/examples',
            'arguments': [
                MODEL_NAME_ARG
            ],
            'returns': [
                {
                    'name': 'examples',
                    'type': 'List[Dict]',
                    'description': 'A list of examples for the model'
                }
            ],
            'decorators': [
                byoml_server_timing_decorator,
                byoml_exception_decorator,
                byoml_retry_decorator,
                return_path_decorator(['example_payloads'])
            ],
            'description': (
                'Fetch the <em>example request input</em> of the named <em>BYOML Model</em>'
            ),
            'links': {
                'doc': 'example-input',
                'apidoc': '',
            },
        },
        'predict': {
            'method': 'POST',
            'url': '/models/{}/predict',
            'arguments': [MODEL_NAME_ARG],
            'returns': [MODEL_INFERENCE_RESULT],
            'decorators': _execute_model_decorators('predictions'),
            'description': (
                'Execute the <em>predict</em> capability of the named <em>BYOML Model</em>'
            ),
            'links': {
                'doc': 'predictions',
                'apidoc': '',
            },
        },
        'regress': {
            'method': 'POST',
            'url': '/models/{}/regress',
            'arguments': [MODEL_NAME_ARG],
            'returns': [MODEL_INFERENCE_RESULT],
            'decorators': _execute_model_decorators('result'),
            'description': (
                'Execute the <em>regress</em> capability of the named  <em>BYOML Model</em>'
            ),
            'links': {
                'doc': 'predictions',
                'apidoc': '',
            },
        },
        'classify': {
            'method': 'POST',
            'url': '/models/{}/classify',
            'arguments': [MODEL_NAME_ARG],
            'returns': [MODEL_INFERENCE_RESULT],
            'decorators': _execute_model_decorators('result'),
            'description': (
                'Execute the <em>classification</em> capability of the named <em>BYOML Model</em>'
            ),
            'links': {
                'doc': 'predictions',
                'apidoc': '',
            },
        },
        'remove': {
            'method': 'DELETE',
            'url': '/models/{}',
            'arguments': [MODEL_NAME_ARG],
            'decorators': [
                byoml_server_timing_decorator,
                byoml_exception_decorator,
                return_body_decorator,
            ],
            'description': 'Remove the named <em>BYOML Model</em>',
            'links': {
                'doc': 'deleting-a-model',
                'apidoc': '',
            },
        },
    }

    def __init__(self, *args, **kwargs):
        """Create a ModelResource."""
        kwargs.pop('timeout', None)
        super().__init__(*args, timeout=DEFAULT_BYOML_MODEL_TIMEOUT, **kwargs)

    @contextmanager
    def _send_model_arguments(
        self, model_name: str, trained_model: Union[PathLike, ByomlModel],
        framework: str = "sklearn",
        framework_version: Optional[str] = None,
        metadata: Optional[Dict] = None,
        work_dir: Optional[PathLike] = None,
        **kwargs
    ):
        """Upload a binary model with given name, framework and description."""
        with ModelZipArchiveBuilder(work_dir) as model_builder:
            with model_builder.save_model_in_dir(trained_model, framework) as model_zip_buffer:
                yield {
                    'body': {
                        "name": model_name,
                        "framework": framework,
                        "framework_version": framework_version,
                        "metadata": json.dumps(metadata or {}),
                    },
                    'files': {
                        "file": ('model.zip', model_zip_buffer.getvalue())
                    },
                    **kwargs
                }

    @contextmanager
    def _send_model_plug_arguments(
        self, model_name: str,
        trained_model: Union[PathLike, ByomlModel],
        framework: str = "sklearn",
        framework_version: Optional[str] = None,
        metadata: Optional[Dict] = None,
        requirements_file: Optional[PathLike] = None,
        requirements: Optional[str] = None,
        lib: Optional[PathLike] = None,
        work_dir: Optional[PathLike] = None,
        **kwargs
    ):
        runtime = self.service.framework.find_runtime(framework, framework_version)
        with ModelPlugArchiveBuilder(work_dir) as builder:
            builder.add_model_spec({
                "name": model_name,
                "version": "0.0.1",
                "metadata": metadata,
                "runtime": runtime['name']
            })
            builder.add_model(trained_model, runtime.get('framework', framework))
            builder.add_requirements(requirements_file, requirements)
            builder.add_lib(lib)
            with builder.create_plug_tar_archive() as (tar_bytes, tar_size):
                headers = kwargs.pop('headers', {})
                headers['Content-Type'] = 'application/tar+gzip'
                headers['Content-Length'] = str(tar_size)
                yield {
                    'body': tar_bytes,  # TODO or 'content': tar_bytes ??
                    'headers': headers,
                    **kwargs
                }

    @suppress_header_decorator('Content-Type')
    def upload(
        self,
        model_name: str,
        trained_model: Union[PathLike, ByomlModel],
        framework: str = "sklearn",
        framework_version: Optional[str] = None,
        metadata: Optional[Dict] = None,
        description: Optional[str] = None,
        requirements_file: Optional[PathLike] = None,
        requirements: Optional[str] = None,
        lib: Optional[PathLike] = None,
        work_dir: Optional[PathLike] = None,
        **kwargs
    ) -> Any:
        """Upload a new machine learning model with given name, framework and description.

Arguments:
    model_name      The name of the model.
    trained_model   The model object (will be serialised to an zip archive before upload),
                    or a file path to the serialized model file or folder.
    framework       One of the supported frameworks (default 'sklearn').
    framework_version
                    A supported framework version, (default `None`,
                    which selects the default server side)
    metadata       User modifiable metadata. Standardised ones are:
                    * 'description' A description of the model.
                    * 'author' The attributed author of the model.
                    * 'title' Used as display title in user interfaces.
    description     Description of the model. (Deprecated: prefer `metadata.description`)
    requirements_file
                    A file containing custom python requirements (above that of the framework)
    requirements    Custom python requirements (above those of the framework).
                    Only one of 'requirements' and 'requirements_file' can be specified.
    lib             A file or folder with custom packages that can be referred to in
                    the requirements file as 'lib/<custom-requirement>'
    work_dir        Optional location of the working directory used to serialize the model.
                    If not specified, a temporary directory is used.
    (other args)    Passed onto the underlying REST request
        """
        if requirements or requirements_file or lib:
            # use the new plug format upload (openfaas only)
            with self._send_model_plug_arguments(
                model_name, trained_model,
                framework=framework,
                framework_version=framework_version,
                metadata={
                    'description': description,
                    **(metadata or {})
                },
                requirements_file=requirements_file,
                requirements=requirements,
                lib=lib,
                work_dir=work_dir,
                **kwargs
            ) as arguments:
                return self._create(**arguments)  # pylint: disable=no-member
        else:
            # legacy format (to be removed after move to openfaas byoml 1.4.0)
            with self._send_model_arguments(
                model_name, trained_model,
                framework=framework,
                framework_version=framework_version,
                metadata={
                    'description': description,
                    **(metadata or {})
                },
                work_dir=work_dir,
                **kwargs
            ) as arguments:
                return self._create(**arguments)  # pylint: disable=no-member

    @suppress_header_decorator('Content-Type')
    def replace(
        self,
        model_name: str,
        trained_model: Union[PathLike, ByomlModel],
        framework: str = "sklearn",
        framework_version: Optional[str] = None,
        metadata: Optional[Dict] = None,
        description: Optional[str] = None,
        work_dir: Optional[PathLike] = None,
        **kwargs
    ) -> Any:
        """Replace a machine learning model with given name, framework and description.

Arguments:
    model_name      The name of the model.
    trained_model   The model object (will be serialised to an zip archive before upload).
    framework       One of the supported frameworks (default 'sklearn').
    framework_version
                    A supported framework version, (default `None`,
                    which selects the default server side)
    metadata       User modifiable metadata. Standardised ones are:
                    * 'description' A description of the model.
                    * 'author' The attributed author of the model.
                    * 'title' Used as display title in user interfaces.
    description     Description of the model. (Deprecated: prefer `metadata.description`)
    work_dir        Optional location of the working directory used to serialize the model.
                    If not specified, a temporary directory is used.
    (other)         Passed onto the underlying REST request.
        """
        with self._send_model_arguments(
                model_name, trained_model,
                framework=framework,
                framework_version=framework_version,
                metadata={
                    'description': description,
                    **(metadata or {})
                },
                work_dir=work_dir,
                **kwargs
        ) as arguments:
            return self._replace(   # pylint: disable=no-member
                model_name,
                **arguments,
            )
