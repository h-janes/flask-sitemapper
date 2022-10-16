from typing import Callable
from functools import wraps
from jinja2 import Environment, BaseLoader
from flask import Flask, url_for, Response
from .templates import SITEMAP, SITEMAP_INDEX


class Sitemapper:
    def __init__(self, app: Flask, https: bool = True, master: bool = False) -> None:
        self.app = app
        self.urlset = []
        self.scheme = "https" if https else "http"
        self.template = SITEMAP_INDEX if master else SITEMAP

    def include(self, **kwargs) -> Callable:
        """A decorator for route functions that calls `add_endpoint`"""

        def decorator(func: Callable) -> Callable:
            self.add_endpoint(func.__name__, **kwargs)

            @wraps(func)
            def wrapper(*args, **kwargs):
                with self.app.app_context():
                    return func(*args, **kwargs)

            return wrapper

        return decorator

    def add_endpoint(self, endpoint: str, **kwargs) -> None:
        """Adds an endpoint to the sitemap"""
        with self.app.app_context():
            url = {"loc": url_for(endpoint, _external=True, _scheme=self.scheme)}

        url.update(kwargs)
        self.urlset.append(url)

    def generate(self) -> Response:
        """Creates a response for the sitemap route function"""
        template = Environment(loader=BaseLoader).from_string(self.template)
        xml = template.render(urlset=self.urlset)
        return Response(xml, mimetype="text/xml")


class SitemapperExtend(Sitemapper):
    def __init__(self, app=None, https: bool = True, master: bool = False):
        super().__init__(app, https, master)
        self.deferred_functions = []

        if app is not None:
            self.init_app(app)

    def init_app(self, app) -> None:
        """ a conventional interface allowing initializing a flask app later"""
        self.app = app

        for deferred in self.deferred_functions:
            deferred(self)

        self.deferred_functions.clear()

    def include(self, **kwargs) -> Callable:
        """A decorator for route functions that calls `add_endpoint`"""

        def decorator(func: Callable) -> Callable:
            self.add_endpoint(func, **kwargs)  # pass in func object instead of func.__name__

            @wraps(func)
            def wrapper(*args, **kwargs):
                with self.app.app_context():
                    return func(*args, **kwargs)

            return wrapper

        return decorator

    def find_endpoint_from_view_func(self, func):
        """ find the endpoint name from a list of registered view functions"""
        for endpoint, view_func in self.app.view_functions.items():
            if func is view_func:  # compare ids of function objects
                return endpoint
        # func not registered as view func
        raise ValueError(f"function {func.__name__} in module {func.__module__} is not a registered view function")

    def add_endpoint(self, view_func, **kwargs) -> None:
        # if flask app is not yet initialized, then register a deferred function and run it later in init_app()
        if not self.app:
            self.deferred_functions.append(
                lambda s: s.add_endpoint(view_func, **kwargs)
            )
            return
        if not isinstance(view_func, str):
            endpoint = self.find_endpoint_from_view_func(view_func)
        else:
            endpoint = view_func
        return super().add_endpoint(endpoint, **kwargs)
