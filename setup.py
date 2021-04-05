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
    entry_points={
        'console_scripts': [
            'mvapi = mvapi:main'
        ]
    },
    install_requires=[
        'alembic>=1.5.4',
        'bcrypt>=3.2',
        'click>=7.1.2',
        'python-dotenv>=0.15',
        'Flask>=1.1',
        'Flask-Cors>=3.0',
        'Flask-SQLAlchemy>=2.4',
        'psycopg2>=2.8',
        'PyJWT>=2.0',
        'shortuuid>=1.0',
        'SQLAlchemy>=1.3',
        'validate-email>=1.3',
        'Werkzeug>=1.0'
    ],
    python_requires='>=3.7',
)

