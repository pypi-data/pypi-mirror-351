import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    name='corona-logistica-moova',
    version='1.0.9',
    packages=['moova'],
    description='Django Moova Integration',
    long_description=README,
    long_description_content_type="text/markdown",
    author='Corona Development Team',
    author_email='rolguin@corona.cl',
    url='https://gitlab.com/linets-projects/python-libraries/django-moova/',
    license='MIT',
    python_requires=">=3.7",
    install_requires=[
        'Django>=3',
        'requests>=2.25.1'
    ]
)
