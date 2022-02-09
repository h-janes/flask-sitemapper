# Flask Sitemapper
Flask Sitemapper is a small Python 3 package that generates XML sitemaps for Flask applications. This allows you to create a nice and fully functional sitemap for your project with very minimal code, as demonstrated below. It is compatible with Flask blueprints.

## Requirements
* Python3
* Flask
* Jinja2

## Installation
```terminal
pip install flask-sitemapper
```

## Usage
### Initialising Flask Sitemapper
The sitemapper must be initialised with the app instance as shown below.

Flask Sitemapper requires `SERVER_NAME` to be specified in the Flask configuration.

By default, HTTPS will be used for all URLs in the sitemap. To change this, specify `https=False` when initialising the sitemapper.
```python
import flask
from flask_sitemapper import Sitemapper

app = flask.Flask("test_app")

# For development, use "127.0.0.1:5000"
app.config["SERVER_NAME"] = "example.com"

sitemapper = Sitemapper(app)
```

If you are using Flask blueprints, you can either list all URLs in a single sitemap by importing the sitemapper instance to your other files or using the `add_endpoint` method (see below), or by creating a sitemap for each blueprint and using a sitemap index (see below).

### Adding URLs to the sitemap
Decorators are added to route functions to include their URLs in the sitemap. These must be included above the Flask decorators.
```python
# Define the homepage route and include it in the sitemap
@sitemapper.include()
@app.route("/")
def r_home():
    return flask.render_template("index.html")
```

You can pass arguments to the decorator to include additional information in the sitemap. Whatever arguments you provide will be included in the URL entry as-is.
```python
@sitemapper.include(
    lastmod = "2022-02-08",
    changefreq = "monthly",
    priority = 1.0,
)
@app.route("/about")
def r_about():
    return flask.render_template("about.html")
```

This example would appear in the sitemap as:
```xml
<url>
  <loc>https://example.com/about</loc>
  <lastmod>2022-02-08</lastmod>
  <changefreq>monthly</changefreq>
  <priority>1.0</priority>
</url>
```

For routes where multiple URL paths are defined, the sitemap will only include the last path.
```python
@sitemapper.include()
@app.route("/shop")  # This won't be included
@app.route("/buy")  # This won't be included
@app.route("/store")  # This will be included
def r_store():
    return "<h1>Store Page</h1>"
```

You can also add Flask endpoints to the sitemap without using their route function. This may be useful when dealing with large or complex projects. Keyword arguments can still be given after the endpoint name.
```python
sitemapper.add_endpoint("r_contact", lastmod="2022-02-09")
```

### Generating and serving the sitemap
To serve your sitemap, you must define a route function that returns `sitemapper.generate()`. Your sitemap will then be avaliable at the URL(s) you specify.

This route should be defined after all routes that are included in the sitemap.
```python
@app.route("/sitemap.xml")
def r_sitemap():
    return sitemapper.generate()
```

### Master Sitemaps
Master sitemaps, or sitemap indexes, are sitemaps that list other sitemaps. These are used if a single sitemap would be too large, or sometimes for organisational purposes. You can create a master sitemapper by specifying `master=True` when initialising your sitemapper.

Note that sitemap indexes have a different syntax to regular sitemaps, so it is important to provide this argument.
```python
master_sitemapper = Sitemapper(app, master=True)
```

You can then decorate your sitemap route functions to add them to the sitemap index.
```python
@master_sitemapper.include()
@app.route("/some_sitemap.xml")
def r_some_sitemap():
    return some_sitemapper.generate()
```

Or add them with `add_endpoint`
```python
@master_sitemapper.add_endpoint("r_some_sitemap")
```

Then create the route for the sitemap index.
```python
@app.route("/sitemap.xml")
def r_sitemap_index():
    return master_sitemapper.generate()
```

For this example, the sitemap index would look like this:
```xml
<?xml version="1.0" encoding="utf-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://example.com/some_sitemap.xml</loc>
  </sitemap>
</sitemapindex>
```
