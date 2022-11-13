"""Provides the `gzip_response` function for compressing Flask `Response` objects"""

from gzip import GzipFile
from io import BytesIO

from flask import Response, request


def gzip_response(response: Response) -> Response:
    """Compresses a Flask `Response` using gzip"""
    # get accepted encodings request header
    accept_encoding = request.headers.get("Accept-Encoding", "").lower()

    # return unedited response if it should not be gzipped
    if (
        response.status_code < 200
        or response.status_code >= 300
        or "gzip" not in accept_encoding
        or "Content-Encoding" in response.headers
    ):
        return response

    # avoid issues with direct_passthrough
    response.direct_passthrough = False

    # gzip the response
    gzip_buffer = BytesIO()
    gzip_file = GzipFile(mode="wb", compresslevel=6, fileobj=gzip_buffer)
    gzip_file.write(response.get_data())
    gzip_file.close()
    response.set_data(gzip_buffer.getvalue())
    response.headers["Content-Encoding"] = "gzip"
    response.headers["Content-Length"] = response.content_length

    return response
