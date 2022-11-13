from functools import wraps
from typing import Callable, Union

from flask import Flask, Response, url_for
from jinja2 import BaseLoader, Environment

from .gzip import gzip_response
from .templates import SITEMAP, SITEMAP_INDEX


class Sitemapper:
    def __init__(
        self, app: Flask = None, https: bool = True, master: bool = False, gzip: bool = False
    ) -> None:
        # process and store provided arguments
        self.scheme = "https" if https else "http"
        self.template = SITEMAP_INDEX if master else SITEMAP
        self.gzip = gzip

        # list of dicts storing the URLs with their parameters for the sitemap
        # e.g. [{"loc": "https://example.com/about", "lastmod": "2022-05-22"}, ...]
        self.urlset = []

        # list of functions to run after extension initilization
        self.deferred_functions = []

        # initialize the extension if the app argument is provided, otherwise, set self.app to None
        self.app = None
        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """A conventional interface allowing initializing a Flask app later"""
        # store the app instance for use elsewhere
        self.app = app

        # run all defered functions
        for deferred in self.deferred_functions:
            deferred(self)

        # clear the deferred functions list
        self.deferred_functions.clear()

    def include(self, **kwargs) -> Callable:
        """A decorator for view functions that adds their URL to the sitemap with any provided arguments"""

        # decorator that calls add_endpoint
        def decorator(func: Callable) -> Callable:
            self.add_endpoint(func, **kwargs)

            @wraps(func)
            def wrapper(*args, **kwargs):
                with self.app.app_context():
                    return func(*args, **kwargs)

            return wrapper

        return decorator

    def __get_endpoint_name(self, func: Callable) -> str:
        """Finds the endpoint name of a view function"""
        # loop over all view functions, comparing function ids to find the endpoint name
        for endpoint, view_func in self.app.view_functions.items():
            if func is view_func:
                return endpoint

        # raise error if func is not registered as a view function
        raise ValueError(
            f"function {func.__name__} in module {func.__module__} is not a registered view function"
        )

    def add_endpoint(self, view_func: Union[Callable, str], **kwargs) -> None:
        """Adds the URL of `view_func` to the sitemap with any provided arguments"""
        # if extension is not yet initialized, register this as a deferred function and return
        if not self.app:
            self.deferred_functions.append(lambda s: s.add_endpoint(view_func, **kwargs))
            return

        # get the endpoint name of view_func
        if not isinstance(view_func, str):
            endpoint = self.__get_endpoint_name(view_func)
        else:
            endpoint = view_func

        # find the URL using url_for and store it in a dict as "loc"
        with self.app.test_request_context():
            url = {"loc": url_for(endpoint, _external=True, _scheme=self.scheme)}

        # add any provided paramaters (e.g. lastmod) to the dict
        url.update(kwargs)

        # append the dict to self.urlset
        self.urlset.append(url)

    def generate(self) -> Response:
        """Creates a Flask `Response` object for the sitemap's view function"""
        # load the jinja template
        template = Environment(loader=BaseLoader).from_string(self.template)

        # render the template with the URLs and parameters
        xml = template.render(urlset=self.urlset)

        # create a flask response
        response = Response(xml, content_type="application/xml")

        # gzip the response if desired
        if self.gzip:
            response = gzip_response(response)

        return response
