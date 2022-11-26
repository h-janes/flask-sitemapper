"""Provides Jinja2 templates for the sitemap and sitemap index"""

SITEMAP = """<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  {%- for url in urls %}
  <url>
    {%- for line in url.xml %}
    {{ line|safe }}
    {%- endfor %}
  </url>
  {%- endfor %}
</urlset>"""

SITEMAP_INDEX = """<?xml version="1.0" encoding="utf-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  {%- for url in urls %}
  <sitemap>
    {%- for line in url.xml %}
    {{ line|safe }}
    {%- endfor %}
  </sitemap>
  {%- endfor %}
</sitemapindex>"""
