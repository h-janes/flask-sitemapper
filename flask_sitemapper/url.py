"""Provides the `URL` class"""

from datetime import datetime
from typing import Callable, Union

from flask import current_app, url_for


class URL:
    """Manages a single URL for the sitemap and its arguments"""

    def __init__(
        self,
        endpoint,
        scheme: str,
        lastmod: Union[str, datetime] = None,
        changefreq: str = None,
        priority: Union[str, int, float] = None,
        url_variables: dict = {},
    ) -> None:
        self.endpoint = endpoint
        self.scheme = scheme
        self.lastmod = lastmod
        self.changefreq = changefreq
        self.priority = priority
        self.url_variables = url_variables

        # convert datetime lastmod to str
        if isinstance(self.lastmod, datetime):
            self.lastmod = self.lastmod.strftime("%Y-%m-%dT%H:%M:%S")

    @property
    def loc(self) -> str:
        """Finds the URL from the endpoint name. Must be called within a request context"""
        return url_for(self.endpoint, _external=True, _scheme=self.scheme, **self.url_variables)

    @property
    def xml(self) -> list:
        """Generates a list of XML lines for this URL's sitemap entry"""
        xml_lines = [f"<loc>{self.loc}</loc>"]
        if self.lastmod:
            xml_lines.append(f"<lastmod>{self.lastmod}</lastmod>")
        if self.changefreq:
            xml_lines.append(f"<changefreq>{self.changefreq}</changefreq>")
        if self.priority:
            xml_lines.append(f"<priority>{self.priority}</priority>")
        return xml_lines


class DynamicEndpoint:
    """Manages URLs for endpoints using URL variables / dynamic routes"""

    def __init__(
        self,
        endpoint,
        scheme: str,
        lastmod: Union[str, datetime, list] = None,
        changefreq: Union[str, datetime, list] = None,
        priority: Union[str, int, float, list] = None,
        url_variables: Union[Callable, dict] = {},
    ) -> None:
        self.endpoint = endpoint
        self.scheme = scheme
        self.lastmod = lastmod
        self.changefreq = changefreq
        self.priority = priority
        self.url_variables = url_variables

    @property
    def urls(self) -> list:
        if isinstance(self.url_variables, Callable):
            # run generator function within app context to get dict
            with current_app.app_context():
                url_variables = self.url_variables()
        else:
            # if not a callable, should be a dict already
            url_variables = self.url_variables

        # list to store URL objects
        urls = []

        # iterate over each set of url variables with a line of code only god understands
        for i, v in enumerate([dict(zip(url_variables, j)) for j in zip(*url_variables.values())]):
            # use sitemap args from the list if a list is provided
            l = self.lastmod[i] if isinstance(self.lastmod, list) else self.lastmod
            c = self.changefreq[i] if isinstance(self.changefreq, list) else self.changefreq
            p = self.priority[i] if isinstance(self.priority, list) else self.priority

            # create URL object and append to the list
            url = URL(self.endpoint, self.scheme, l, c, p, v)
            urls.append(url)

        return urls
