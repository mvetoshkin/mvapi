import re

from setuptools import find_packages, setup

with open('./mvapi/__init__.py') as file:
    version = re.search(r'__version__ = \'(.*?)\'', file.read()).group(1)

setup(
    name='mvapi',
    version=version,
    author='Mikhail Vetoshkin',
    author_email='mikhail@vetoshkin.dev',
    description='Skeleton for a JSON API project',
    url='https://github.com/mvetoshkin/mvapi',
    packages=find_packages(),
    install_requires=[
        'bcrypt>=3.2',
        'python-dotenv>=0.15',
        'Flask>=1.1',
        'Flask-Cors>=3.0',
        'Flask-Migrate>=2.6',
        'Flask-SQLAlchemy>=2.4',
        'PyJWT>=2.0',
        'shortuuid>=1.0',
        'SQLAlchemy>=1.3',
        'validate-email>=1.3',
        'Werkzeug>=1.0'
    ],
    python_requires='>=3.7',
)

