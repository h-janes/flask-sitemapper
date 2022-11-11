import pathlib

from setuptools import find_packages, setup

VERSION = "1.3.2"

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="flask-sitemapper",
    version=VERSION,
    license="MIT",
    # Metadata
    author="H Janes",
    author_email="dev@hjanes.com",
    description="Sitemap generator for Flask applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["flask", "python", "sitemap"],
    platforms=[""],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Framework :: Flask",
        "Operating System :: OS Independent",
    ],
    # Packages
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=["flask", "jinja2"],
    python_requires=">=3.6",
    # URLs
    url="https://github.com/h-janes/flask-sitemapper",
    download_url="https://pypi.org/project/flask-sitemapper/",
    project_urls={
        "Bug Reports": "https://github.com/h-janes/flask-sitemapper/issues",
        "Source": "https://github.com/h-janes/flask-sitemapper",
    },
)
