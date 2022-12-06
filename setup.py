try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from os import path

long_desc = open(path.join(path.dirname(__file__), "README.md"), "r").read()

setup(name="fish", version="1.1",
      url="http://sendapatch.se/",
      author="Ludvig Ericson",
      author_email="ludvig@sendapatch.se",
      description="Animating fish (and birds) for progress bars",
      long_description=long_desc,
      use_2to3=True,
      py_modules=["fish"])
