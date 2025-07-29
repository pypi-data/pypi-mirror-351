import os
import re
from setuptools import setup, find_packages
from io import open

with open(os.path.join(os.path.dirname(__file__), 'cloudscraper25', '__init__.py')) as fp:
    VERSION = re.match(r'.*__version__ = \'(.*?)\'', fp.read(), re.S).group(1)

with open('README.md', 'r', encoding='utf-8') as fp:
    readme = fp.read()

setup(
    name = 'cloudscraper25',
    author = 'Zied Boughdir, VeNoMouS',
    author_email = 'ziedboughdir@gmail.com',
    version=VERSION,
    packages = ['cloudscraper25', 'cloudscraper25.captcha', 'cloudscraper25.interpreters', 'cloudscraper25.user_agent'],
    py_modules = [],
    description = 'Enhanced Python module to bypass Cloudflare\'s anti-bot page with support for v2 challenges, proxy rotation, and stealth mode.',
    long_description=readme,
    long_description_content_type='text/markdown',
    url = 'https://github.com/zinzied/cloudscraper25',
    keywords = [
        'cloudflare',
        'scraping',
        'ddos',
        'scrape',
        'webscraper',
        'anti-bot',
        'waf',
        'iuam',
        'bypass',
        'challenge'
    ],
    include_package_data = True,
    install_requires = [
        'requests >= 2.9.2',
        'requests_toolbelt >= 0.9.1',
        'pyparsing >= 2.4.7',
        'pyOpenSSL >= 22.0.0',
        'pycryptodome >= 3.15.0',
        'websocket-client >= 1.3.3',
        'js2py >= 0.74'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
