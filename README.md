# Flask Sitemapper
![PyPI - Downloads](https://img.shields.io/pypi/dw/flask-sitemapper?color=%23379358&label=Downloads&style=for-the-badge)

Flask Sitemapper is a small Python 3 package that generates XML sitemaps for Flask applications. This allows you to create a fully functional sitemap for your project with minimal code, as demonstrated below. It is compatible with Flask blueprints.

For more information about sitemaps and the XML schema, visit [sitemaps.org](https://www.sitemaps.org).

## Installation
Flask Sitemapper requires Python 3.7 or newer. The Python packages `flask` and `jinja2` are also required, and will be installed automatically.

The latest version can be installed from PyPi with pip as shown below.
```terminal
pip install flask-sitemapper
```

## Usage
### Initialising Flask Sitemapper
The sitemapper must be initialised with the app instance as shown below.

By default, HTTPS will be used for all URLs in the sitemap. To change this, specify `https=False` when creating the `Sitemapper` instance.

#### Recommended Method
```python
import flask
from flask_sitemapper import Sitemapper

# create sitemapper instance
sitemapper = Sitemapper()

# create app
app = flask.Flask("test_app")

# initialize with app
sitemapper.init_app(app)
```

#### Alternative Method
```python
import flask
from flask_sitemapper import Sitemapper

# create app
app = flask.Flask("test_app")

# create instance and initialize with app
sitemapper = Sitemapper(app)
```

### Adding URLs to the Sitemap
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

### Using With Flask blueprints
* Create your `Sitemapper` instance(s) in a seperate file or otherwise avoiding circular imports.

* Import and use the instance(s) in your blueprints.

* Import the instance(s) when creating your flask app and initialize with `sitemapper.init_app(app)` ***after*** registering your blueprints.

You can also add Flask endpoints to the sitemap by using their endpoint name as shown below. Keyword arguments can still be given after the endpoint name.
```python
sitemapper.add_endpoint("r_contact", lastmod="2022-02-09")
```

### Generating and Serving the Sitemap
To serve your sitemap, you must define a route function that returns `sitemapper.generate()`. Your sitemap will then be avaliable at the URL(s) you specify.

This route should be defined after all routes that are included in the sitemap.
```python
@app.route("/sitemap.xml")
def r_sitemap():
    return sitemapper.generate()
```

### Sitemap Indexes
Sitemap indexes are sitemaps that list other sitemaps. These are used if a single sitemap would be too large, or sometimes for organisational purposes. You can create a master sitemapper, which generates a sitemap index, by specifying `master=True` when creating the instance.

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

### Example App
```python
import flask
from flask_sitemapper import Sitemapper

sitemapper = Sitemapper()

app = flask.Flask("test_app")

sitemapper.init_app(app)

@sitemapper.include()
@app.route("/")
def r_home():
    return flask.render_template("index.html")

@sitemapper.include(
    lastmod = "2022-02-08",
    changefreq = "monthly",
    priority = 1.0,
)
@app.route("/about")
def r_about():
    return flask.render_template("about.html")

@app.route("/sitemap.xml")
def r_sitemap():
    return sitemapper.generate()

app.run()
```

## Development & Contributing
Thank you for contributing to the project! All issues and pull requests are highly appreciated.

### Development Requirements
* [Python](https://www.python.org) 3.7 or later
* [Poetry](https://python-poetry.org) for package management and building

The following Python libraries will be installed automatically to a virtual environment by poetry during setup.
* flask
* jinja2
* black
* isort
* pytest
* requests

### Project Setup
Install `poetry` if not already installed.
```terminal
pip install poetry
```

Clone the repository and enter the repository's directory.
```terminal
git clone https://github.com/h-janes/flask-sitemapper
cd flask-sitemapper
```

Create the poetry virtual environment and install dependencies.
```terminal
poetry install
```
You may want to configure your editor to use the virtual environment for linting and debugging. You can find the path of the virtual environment with the command:
```terminal
poetry env info --path
```

### Code Style
Flask Sitemapper uses `black` for code formatting and `isort` for import ordering.

It is recommended that you configure your editor to run `black` and `isort` on save, making sure that they access the configurations defined in `pyproject.toml`

Otherwise, you should ensure that your code conforms to these style standards before submitting a pull request.

### Testing
Tests are stored in the `tests` directory. You should ensure that all tests are passing before creating a pull request. If you create a pull request with new features, creating new tests for your additions is highly appreciated. You can run all tests with the command: 
```terminal
poetry run pytest
```

### Building
The project can be built with the command:
```terminal
poetry build
```
This should generate a `dist` directory containing a `.tar.gz` file and a `.whl` file.