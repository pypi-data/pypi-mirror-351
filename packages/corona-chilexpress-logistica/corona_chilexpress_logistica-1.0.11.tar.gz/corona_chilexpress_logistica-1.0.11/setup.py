import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    name='corona-chilexpress-logistica',
    version='1.0.11',
    packages=['chilexpress'],
    description='Django Chilexpress integration',
    long_description=README,
    long_description_content_type="text/markdown",
    author='Corona Development Team',
    author_email='rolguin@corona.cl',
    url='https://gitlab.com/corona-projects/python-libraries/django-chilexpress/',
    license='MIT',
    python_requires=">=3.7",
    install_requires=[
        'Django>=3',
        'requests>=2.25.1'
    ]
)
