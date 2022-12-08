"""Provides the `URL` class"""

from datetime import datetime
from typing import Union

from flask import url_for


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
