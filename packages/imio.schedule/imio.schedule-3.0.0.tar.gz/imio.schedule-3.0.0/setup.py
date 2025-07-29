# -*- coding: utf-8 -*-
"""Installer for the imio.schedule package."""

from setuptools import find_packages
from setuptools import setup


long_description = (
    open("README.rst").read()
    + "\n"
    + "Contributors\n"
    + "============\n"
    + "\n"
    + open("CONTRIBUTORS.rst").read()
    + "\n"
    + open("CHANGES.rst").read()
    + "\n"
)


setup(
    name="imio.schedule",
    version="3.0.0",
    description="Schedule for imio products",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # Get more from https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone",
    author="Simon Delcourt",
    author_email="simon.delcourt@imio.be",
    url="https://pypi.python.org/pypi/imio.schedule",
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["imio"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "collective.eeafaceted.collectionwidget",
        "collective.faceted.task",
        "collective.wfadaptations",
        "collective.z3cform.datagridfield",
        "imio.dashboard",
        "plone.api",
        "plone.app.dexterity",
        "plone.restapi",
        "Products.cron4plone",
        "setuptools",
        "workalendar",
    ],
    extras_require={
        "test": [
            "Mock",
            "plone.app.testing",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
