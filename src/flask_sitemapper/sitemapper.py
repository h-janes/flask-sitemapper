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
