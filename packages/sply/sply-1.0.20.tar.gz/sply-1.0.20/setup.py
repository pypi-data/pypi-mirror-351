# -*- coding: utf-8 -*-
from setuptools import setup

setup_kwargs = {
    'name': 'sply',
    'version': '1.0.20',
    'description': 'a bridge between real and simulated python interpreters',
    'long_description': '',
    'author': 'Richard Benson',
    'author_email': 'richardbenson91477@protonmail.com',
    'maintainer': 'Richard Benson',
    'maintainer_email': 'richardbenson91477@protonmail.com',
    'url': 'https://github.com/richardbenson91477/sply',
    'packages': ['sply', 'sply/overmind'],
    'package_data': {'': ['*']},
    'python_requires': '>=3.8',
    'scripts': ['bin/sply_chat_interact.py', 'bin/sply_double_chat.py']
}

setup(**setup_kwargs)

