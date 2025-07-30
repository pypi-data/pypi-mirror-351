from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.4'
DESCRIPTION = 'Make it simple'
LONG_DESCRIPTION = long_description

# Setting up
setup(
    name="MakeItSimplerJKX",
    version=VERSION,
    author="juckex",
    author_email="<juliusstensso@gmail.com>",
    packages=find_packages(),
    install_requires=['langchain>=0.1.0', 'langchain-community>=0.0.10', 'openai>=1.0.0', 'python-dotenv>=1.0.0'],
    keywords=['python', 'AI', 'chat', 'simple', 'agent'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
