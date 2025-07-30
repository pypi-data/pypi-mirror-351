# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import os
from setuptools import setup

README = """
See the README on `GitHub
<https://github.com/uw-it-aca/django-person-client>`_.
"""

version_path = 'uw_person_client/VERSION'
VERSION = open(os.path.join(os.path.dirname(__file__), version_path)).read()
VERSION = VERSION.replace("\n", "")

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

url = "https://github.com/uw-it-aca/django-person-client"
setup(
    name='Django-Person-Client',
    version=VERSION,
    packages=['uw_person_client'],
    author="UW-IT Student & Educational Technology Services",
    author_email="aca-it@uw.edu",
    include_package_data=True,
    install_requires=[
        'django>=4.2,<6',
        'psycopg2',
        'uw-restclients-pws',
    ],
    license='Apache License, Version 2.0',
    description=('A UW Person Client Django app'),
    long_description=README,
    url=url,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
