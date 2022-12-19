# Flask Sitemapper
Flask Sitemapper is a Python 3 package that generates XML sitemaps for Flask applications. This allows you to create fully functional sitemaps and sitemap indexes for your Flask projects with minimal code.

You can install the [latest version](https://pypi.org/project/flask-sitemapper/) of Flask Sitemapper with pip:
```terminal
pip install flask-sitemapper
```

For documentation (including for contributors), see [the wiki](https://github.com/h-janes/flask-sitemapper/wiki).

# Features
* Easily generate and serve XML sitemaps and sitemap indexes for your Flask apps
* Include URLs in your sitemaps by adding a decorator to their route/view functions
* Serve your sitemap on any URL you choose
* Include lastmod, changefreq, and priority information in your sitemaps
* Specify whether to use HTTP or HTTPS for the URLs in your sitemaps
* Compress your sitemaps using GZIP
* Create multiple sitemaps and sitemap indexes for the same app
* Supports apps using Flask blueprints
* Supports apps serving multiple domains
* Supports dynamic routes
* Works with many different app structures

# Sitemaps
> Sitemaps are an easy way for webmasters to inform search engines about pages on their sites that are available for crawling. In its simplest form, a Sitemap is an XML file that lists URLs for a site along with additional metadata about each URL (when it was last updated, how often it usually changes, and how important it is, relative to other URLs in the site) so that search engines can more intelligently crawl the site.
> &mdash; <cite>[sitemaps.org](https://www.sitemaps.org)</cite>

For more information about sitemaps and the sitemap protocol, visit [sitemaps.org](https://www.sitemaps.org)

# Basic Code Example
```python
import flask
from flask_sitemapper import Sitemapper

sitemapper = Sitemapper()

app = flask.Flask(__name__)
sitemapper.init_app(app)

@sitemapper.include(lastmod="2022-02-08")
@app.route("/")
def home():
  return flask.render_template("home.html")

@sitemapper.include(lastmod="2022-03-19")
@app.route("/about")
def about():
  return flask.render_template("about.html")

@app.route("/sitemap.xml")
def sitemap():
  return sitemapper.generate()

app.run()
```

With the above code running on localhost, `http://localhost/sitemap.xml` will serve the following XML sitemap:
```xml
<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://localhost/</loc>
    <lastmod>2022-02-08</lastmod>
  </url>
  <url>
    <loc>https://localhost/about</loc>
    <lastmod>2022-03-19</lastmod>
  </url>
</urlset>
```
