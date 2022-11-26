"""Provides the `URL` and `Sitemapper` classes"""

from functools import wraps
from typing import Callable, Union

from flask import Flask, Response, url_for
from jinja2 import BaseLoader, Environment

from .gzip import gzip_response
from .templates import SITEMAP, SITEMAP_INDEX


class URL:
    """Stores a URL for the sitemap with its arguments"""

    def __init__(
        self,
        endpoint,
        scheme: str,
        lastmod: str = None,
        changefreq: str = None,
        priority: Union[str, int, float] = None,
    ) -> None:
        self.endpoint = endpoint
        self.scheme = scheme
        self.lastmod = lastmod
        self.changefreq = changefreq
        self.priority = priority

    @property
    def loc(self) -> str:
        """Finds the URL from the endpoint name. Must be called within a request context"""
        return url_for(self.endpoint, _external=True, _scheme=self.scheme)

    @property
    def xml(self) -> str:
        """Generates a list of XML lines for this URL's sitemap entry"""
        xml_lines = [f"<loc>{self.loc}</loc>"]
        if self.lastmod:
            xml_lines.append(f"<lastmod>{self.lastmod}</lastmod>")
        if self.changefreq:
            xml_lines.append(f"<changefreq>{self.changefreq}</changefreq>")
        if self.priority:
            xml_lines.append(f"<priority>{self.priority}</priority>")
        return xml_lines


class Sitemapper:
    """The main class for this extension which manages and creates a sitemap"""

    def __init__(self, app: Flask = None, https: bool = True, master: bool = False) -> None:
        # process and store provided arguments
        self.scheme = "https" if https else "http"
        self.template = SITEMAP_INDEX if master else SITEMAP

        # list of URL objects to list in the sitemap
        self.urls = []

        # list of functions to run after extension initialization
        self.deferred_functions = []

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
        self, lastmod: str = None, changefreq: str = None, priority: Union[str, int, float] = None
    ) -> Callable:
        """A decorator for view functions to add their URL to the sitemap"""

        # decorator that calls add_endpoint
        def decorator(func: Callable) -> Callable:
            self.add_endpoint(func, lastmod=lastmod, changefreq=changefreq, priority=priority)

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
        lastmod: str = None,
        changefreq: str = None,
        priority: Union[str, int, float] = None,
    ) -> None:
        """Adds the URL of `view_func` to the sitemap with any provided arguments"""
        # if extension is not yet initialized, register this as a deferred function and return
        if not self.app:
            self.deferred_functions.append(
                lambda s: s.add_endpoint(
                    view_func, lastmod=lastmod, changefreq=changefreq, priority=priority
                )
            )
            return

        # get the endpoint name of view_func
        if not isinstance(view_func, str):
            endpoint = self.__get_endpoint_name(view_func)
        else:
            endpoint = view_func

        # create a URL object and append it to self.urls
        url = URL(endpoint, self.scheme, lastmod=lastmod, changefreq=changefreq, priority=priority)
        self.urls.append(url)

    def generate(self, gzip: bool = False) -> Response:
        """Creates a Flask `Response` object for the XML sitemap"""
        # load the jinja template
        template = Environment(loader=BaseLoader).from_string(self.template)

        # render the template with the URLs and parameters
        xml = template.render(urls=self.urls)

        # create a flask response
        response = Response(xml, content_type="application/xml")

        # gzip the response if desired
        if gzip:
            response = gzip_response(response)

        return response
