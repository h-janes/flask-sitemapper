from typing import Callable
from functools import wraps
from jinja2 import Environment, BaseLoader
from flask import Flask, url_for, Response

# Jinja template for the sitemap
SITEMAP = """<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
  {% for url in urlset %}
    <url>
      {% for arg, value in url.items() %}
        <{{arg}}>{{ value }}</{{arg}}>
      {% endfor %}
    </url>
  {% endfor %}
</urlset>"""

# Sitemap counter for unique endpoint names
NUMBER_OF_SITEMAPS = 0


class Sitemapper:
    def __init__(self, app: Flask, url_path: str = "/sitemap.xml") -> None:
        self.url_path = url_path
        self.app = app
        self.urlset = []

        # Disgusting code to allow for mulitple sitemaps
        def create_sitemap_route() -> Callable:
            def sitemap_route() -> Response:
                template = Environment(loader=BaseLoader).from_string(SITEMAP)
                xml = template.render(urlset=self.urlset)
                return Response(xml, mimetype="text/xml")

            global NUMBER_OF_SITEMAPS
            sitemap_route.__name__ = f"sitemap_route_{NUMBER_OF_SITEMAPS}"
            NUMBER_OF_SITEMAPS += 1
            return sitemap_route

        # Add sitemap route to the app
        self.app.add_url_rule(self.url_path, view_func=create_sitemap_route())

    def include(self, **kwargs) -> Callable:
        """A decorator for route functions to add them to the sitemap"""

        def decorator(func: Callable) -> Callable:
            with self.app.app_context():
                url = {
                    "loc": url_for(
                        func.__name__,
                        _external=True,
                        _scheme=self.app.config.get("PREFFERED_URL_SCHEME", "http"),
                    )
                }

            url.update(kwargs)
            self.urlset.append(url)

            @wraps(func)
            def wrapper(*args, **kwargs):
                with self.app.app_context():
                    return func(*args, **kwargs)

            return wrapper

        return decorator
