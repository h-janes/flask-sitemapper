# Jinja templates for the sitemap and sitemap index

SITEMAP = """<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  {%- for url in urlset %}
  <url>
    {%- for arg, value in url.items() %}
    <{{arg}}>{{ value }}</{{arg}}>
    {%- endfor %}
  </url>
  {%- endfor %}
</urlset>"""

SITEMAP_INDEX = """<?xml version="1.0" encoding="utf-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  {%- for url in urlset %}
  <sitemap>
    {%- for arg, value in url.items() %}
    <{{arg}}>{{ value }}</{{arg}}>
    {%- endfor %}
  </sitemap>
  {%- endfor %}
</sitemapindex>"""
