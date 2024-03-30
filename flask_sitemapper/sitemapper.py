"""Provides the `Sitemapper` class"""

from datetime import datetime
from functools import wraps
from typing import Callable, Union

from flask import Flask, Response
from jinja2 import BaseLoader, Environment

from .gzip import gzip_response
from .templates import SITEMAP, SITEMAP_INDEX
from .url import URL, DynamicEndpoint


class Sitemapper:
    """The main class for this extension which manages and creates a sitemap"""

    def __init__(self, app: Flask = None, https: bool = True, master: bool = False) -> None:
        # process and store provided arguments
        self.scheme = "https" if https else "http"
        self.template = SITEMAP_INDEX if master else SITEMAP

        # list of URL objects to list in the sitemap
        self.urls = []

        # list of DynamicEndpoint objects for endpoints suing url variables
        self.dynamic_endpoints = []

        # list of functions to run after extension initialization
        self.deferred_functions = []

        # store the finished XML for the sitemap
        self.cache_xml = True
        self.cached_xml = None

        # initialize the extension if the app argument is provided, otherwise, set self.app to None
        self.app = None
        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """A conventional interface allowing initializing a Flask app later"""
        # store the app instance for use elsewhere
        self.app = app

        # run all deferred functions
        for deferred in self.deferred_functions:
            deferred(self)

        # clear the deferred functions list
        self.deferred_functions.clear()

    def include(
        self,
        lastmod: Union[str, datetime, list] = None,
        changefreq: Union[str, list] = None,
        priority: Union[str, int, float, list] = None,
        url_variables: Union[Callable, dict] = {},
    ) -> Callable:
        """A decorator for view functions to add their URL to the sitemap"""

        # decorator that calls add_endpoint
        def decorator(func: Callable) -> Callable:
            self.add_endpoint(func, lastmod, changefreq, priority, url_variables)

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
            f"{func.__name__} in module {func.__module__} is not a registered view function"
        )

    def add_endpoint(
        self,
        view_func: Union[Callable, str],
        lastmod: Union[str, datetime, list] = None,
        changefreq: Union[str, list] = None,
        priority: Union[str, int, float, list] = None,
        url_variables: Union[Callable, dict] = {},
    ) -> None:
        """Adds the URL of `view_func` to the sitemap with any provided arguments"""
        # if extension is not yet initialized, register this as a deferred function and return
        if not self.app:
            self.deferred_functions.append(
                lambda s: s.add_endpoint(view_func, lastmod, changefreq, priority, url_variables)
            )
            return

        # get the endpoint name of view_func
        if not isinstance(view_func, str):
            endpoint = self.__get_endpoint_name(view_func)
        else:
            endpoint = view_func

        # if url variables are provided (for dynamic routes)
        if url_variables:
            # disable xml caching if a callable value is provided
            if isinstance(url_variables, Callable):
                self.cache_xml = False

            # create a DynamicEndpoint object
            dynamic_endpoint = DynamicEndpoint(
                endpoint, self.scheme, lastmod, changefreq, priority, url_variables
            )
            self.dynamic_endpoints.append(dynamic_endpoint)
        else:
            # create a URL object without url variables and append it to self.urls
            url = URL(endpoint, self.scheme, lastmod, changefreq, priority)
            self.urls.append(url)

    def generate(self, gzip: bool = False) -> Response:
        """Creates a Flask `Response` object for the XML sitemap"""

        # check for cached xml
        if self.cache_xml and self.cached_xml:
            xml = self.cached_xml
        else:
            # get all urls for the sitemap
            urls = self.urls.copy()
            for dynamic_endpoint in self.dynamic_endpoints:
                urls += dynamic_endpoint.urls

            # create the final xml document
            template = Environment(loader=BaseLoader).from_string(self.template)
            xml = template.render(urls=urls)

            # cache the xml if enabled
            if self.cache_xml:
                self.xml = xml

        # create a flask response
        response = Response(xml, content_type="application/xml")

        # gzip the response if desired
        if gzip:
            response = gzip_response(response)

        return response
