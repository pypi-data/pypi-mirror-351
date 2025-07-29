"""REST definitions for handling content from the 'storage' service objects."""
__docformat__ = "google"

from typing import Optional, Any, Union, IO, List, Dict
from pathlib import Path
import os

import httpx
import httpx._types as _http_types

from tqdm import tqdm

from waylay.exceptions import RestResponseError, RestRequestError
from waylay.service import WaylayResource, WaylayRESTService


_http = httpx


class ContentTool(WaylayResource):
    """Tool for handling content from of the 'storage' service objects using signed get and put links."""

    service: WaylayRESTService

    actions: Dict[str, Any] = {
        'put': {
            'wrapped_actions': []
        },
        'get': {
            'wrapped_actions': []
        }
    }

    def put(
        self,
        bucket: str,
        path: str,
        content_type: Optional[str] = None,
        content: Optional[_http_types.RequestContent] = None,
        json: Any = None,
        from_file: Optional[Union[str, os.PathLike]] = None,
        progress: bool = True,
        headers: Optional[_http_types.HeaderTypes] = None,
        raw: bool = False,
        **kwargs
    ) -> Union[_http.Response, str]:
        """Store the content of a storage object.

Content can be specified with (exactly) one of the attributes 'from_file', 'content' or 'json'.

This method gets a signed url (see storage.object.sign_put),
and uploads the object content to the object store.

Arguments:
    bucket          The name of the bucket.
    path            The object path for the uploaded content.
    content_type    [optional] The content type with which this content will be available.
    content         A byte array or byte stream. With streaming data, you will need
                    to provide a 'content-length' header.
    json            A data structure as to be uploaded with JSON encoding.
    from_file       A file path of the file content that needs to be uploaded.
    progress        [optional, bool] If true, the client will show a progress bar.
    headers         [optional] Additional headers to be used for the upload.
    raw             [optional, bool] If True, the HTTP response object is returned,
                    even in case of failures. Otherwise, return the status text or
                    raises errors on failure.
    kwargs          Additional attributes forwarded to the 'sign_get' request.
        """
        params = kwargs.pop('params', {})
        params.update(kwargs)
        headers = _http.Headers(headers)
        if content_type:
            params['content_type'] = content_type
            headers.update({'content-type': content_type})

        upload_url = self.service.object.sign_put(bucket, path, params=params)

        if sum(input is not None for input in [content, json, from_file]) != 1:
            raise RestRequestError(
                "Only one of the 'content', 'json' or 'from_file' arguments"
                " should be specified."
            )

        if progress:
            print(
                f'Uploading content to {bucket}/{path} ...'
            )
        if from_file:
            file_path = Path(from_file)
            headers.update({'content-length': format(file_path.stat().st_size)})
            with open(from_file, 'rb') as file_content:
                response = _http.put(
                    upload_url,
                    content=file_content,
                    headers=headers
                )
        else:
            response = _http.put(
                upload_url,
                content=content,
                json=json,
                headers=headers
            )

        if progress:
            print('... done.')

        if raw:
            return response

        self._raise_for_status(f'Failed to upload for {bucket}/{path}', response)
        return response.reason_phrase

    def _write_response_to_file_with_progress(self, response: _http.Response, file_stream: IO):
        total = int(response.headers['Content-Length'])
        with tqdm(total=total, unit_scale=True, unit_divisor=1024, unit="B") as progress:
            num_bytes_downloaded = response.num_bytes_downloaded
            for chunk in response.iter_bytes():
                file_stream.write(chunk)
                progress.update(response.num_bytes_downloaded - num_bytes_downloaded)
                num_bytes_downloaded = response.num_bytes_downloaded

    def _write_response_to_file(self, response: _http.Response, file_stream: IO):
        for chunk in response.iter_bytes():
            file_stream.write(chunk)

    def _raise_for_status(self, message: str, response: _http.Response):
        try:
            response.raise_for_status()
        except _http.HTTPStatusError as exc:
            raise RestResponseError(message, exc.response) from exc

    def _get_to_file(self, get_url: str, to_file: Path, progress: bool):
        with open(to_file, 'wb') as download_stream:
            with _http.stream('GET', get_url) as response:
                if response.status_code >= 300:
                    return response
                if progress:
                    self._write_response_to_file_with_progress(response, download_stream)
                else:
                    self._write_response_to_file(response, download_stream)
                return response

    def get(
        self,
        bucket: str,
        path: str,
        to_file: Optional[Union[str, os.PathLike]] = None,
        progress: bool = True,
        headers: Optional[_http_types.HeaderTypes] = None,
        raw: bool = False,
        **kwargs
    ) -> Union[_http.Response, Path]:
        """Retrieve the content of a storage object.

This method gets the signed_url (see storage.object.sign_get),
and downloads the object content from the given url to the object store.

Arguments:
    bucket          The name of the bucket.
    path            The object path for the content to be downloaded.
    to_file         A local file path to which the content should be saved.
                    If succesfull, will return a 'Path' object to that file.
    progress        [optional, bool] If true, the client will show a progress bar.
    headers         [optional] Additional headers to be used for the download.
    raw             [optional, bool] If 'True', the HTTP response object is returned,
                    even in case of failures. Otherwise, raises errors on failure.

    kwargs          Additional attributes forwarded to the 'sign_get' request.

Returns:
    If 'to_file' is specified: a 'Path' object representing the download location.
    Otherwise, w response object having having a properties like
        'content', 'text', 'status_code', 'headers'
    and a
        'json()'
    method to extract the data.
        """
        params = kwargs.pop('params', {})
        params.update(kwargs)
        get_url = self.service.object.sign_get(bucket, path, params=params)

        if to_file:
            response = self._get_to_file(get_url, Path(to_file), progress)
        else:
            response = _http.get(get_url, headers=headers)

        if raw:
            return response

        self._raise_for_status(f'Failed to retrieve content for {bucket}/{path}', response)

        if to_file:
            return Path(to_file).absolute()

        return response
