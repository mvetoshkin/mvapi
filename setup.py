import re

from setuptools import find_packages, setup

with open('./mvapi/version.py') as file:
    version = re.search(r'version = \'(.*?)\'', file.read()).group(1)

setup(
    name='mvapi',
    version=version,
    author='Mikhail Vetoshkin',
    author_email='mikhail@vetoshkin.dev',
    description='Skeleton for a JSON API project',
    url='https://git.vetoshkin.dev/mvapi',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'mvapi = mvapi:main'
        ]
    },
    install_requires=[
        'alembic == 1.7.5',
        'bcrypt == 3.2.0',
        'click == 8.0.3',
        'flask == 2.0.2',
        'flask-cors == 3.0.10',
        'inflect == 5.4.0',
        'jinja2 == 3.0.2',
        'psycopg2 == 2.9.3',
        'pyjwt == 2.3.0',
        'python-dateutil==2.8.2',
        'python-dotenv == 0.19.1',
        'shortuuid == 1.0.8',
        'sqlalchemy == 1.4.28',
        'validate-email == 1.3',
        'werkzeug == 2.1.0',
    ],
    python_requires='>=3.9',
)
