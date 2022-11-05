from typing import Callable, Union
from functools import wraps
from jinja2 import Environment, BaseLoader
from flask import Flask, url_for, Response
from .templates import SITEMAP, SITEMAP_INDEX


class Sitemapper:
    def __init__(self, app: Flask = None, https: bool = True, master: bool = False) -> None:
        self.app = None
        self.urlset = []
        self.scheme = "https" if https else "http"
        self.template = SITEMAP_INDEX if master else SITEMAP
        self.deferred_functions = []

        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """A conventional interface allowing initializing a flask app later"""
        self.app = app

        for deferred in self.deferred_functions:
            deferred(self)

        self.deferred_functions.clear()

    def include(self, **kwargs) -> Callable:
        """A decorator for view functions that calls `add_endpoint`"""

        def decorator(func: Callable) -> Callable:
            self.add_endpoint(func, **kwargs)

            @wraps(func)
            def wrapper(*args, **kwargs):
                with self.app.app_context():
                    return func(*args, **kwargs)

            return wrapper

        return decorator

    def find_endpoint_from_view_func(self, func: Callable) -> str:
        """Find the endpoint name from a list of registered view functions"""
        for endpoint, view_func in self.app.view_functions.items():
            if func is view_func:  # compare ids of function objects
                return endpoint

        # func not registered as view func
        raise ValueError(f"function {func.__name__} in module {func.__module__} is not a registered view function")

    def add_endpoint(self, view_func: Union[Callable, str], **kwargs) -> None:
        """Adds the URL of `view_func` to the sitemap with any provided arguments"""
        # if flask app is not yet initialized, then register a deferred function and run it later in init_app()
        if not self.app:
            self.deferred_functions.append(lambda s: s.add_endpoint(view_func, **kwargs))
            return

        if not isinstance(view_func, str):
            endpoint = self.find_endpoint_from_view_func(view_func)
        else:
            endpoint = view_func

        # add url of view_func and any kwargs to urlset
        with self.app.test_request_context():
            url = {"loc": url_for(endpoint, _external=True, _scheme=self.scheme)}

        url.update(kwargs)
        self.urlset.append(url)

    def generate(self) -> Response:
        """Creates a flask `Response` object for the sitemap's view function"""
        template = Environment(loader=BaseLoader).from_string(self.template)
        xml = template.render(urlset=self.urlset)
        return Response(xml, mimetype="text/xml")
