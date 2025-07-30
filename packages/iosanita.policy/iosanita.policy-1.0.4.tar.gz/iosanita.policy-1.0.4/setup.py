# -*- coding: utf-8 -*-
"""Installer for the iosanita.policy package."""

from setuptools import find_packages
from setuptools import setup


long_description = "\n\n".join(
    [
        open("README.rst").read(),
        open("CONTRIBUTORS.rst").read(),
        open("CHANGES.rst").read(),
    ]
)


setup(
    name="iosanita.policy",
    version="1.0.4",
    description="An add-on for Plone",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="Python Plone CMS",
    author="RedTurtle Technology",
    author_email="sviluppo@redturtle.it",
    url="https://github.com/collective/iosanita.policy",
    project_urls={
        "PyPI": "https://pypi.org/project/iosanita.policy/",
        "Source": "https://github.com/collective/iosanita.policy",
        "Tracker": "https://github.com/collective/iosanita.policy/issues",
        # 'Documentation': 'https://iosanita.policy.readthedocs.io/en/latest/',
    },
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["iosanita"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[
        "setuptools",
        # -*- Extra requirements: -*-
        "plone.api>=1.8.4",
        "iosanita.contenttypes",
        "collective.volto.enhancedlinks",
        "collective.feedback",
        "collective.volto.slimheader",
        "iw.rejectanonymous",
        "collective.volto.dropdownmenu",
        "collective.volto.socialsettings",
        "collective.volto.secondarymenu",
        "redturtle.faq",
        "redturtle.bandi",
        "redturtle.rssservice",
        "collective.volto.subsites",
        "redturtle.voltoplugin.editablefooter",
        "collective.volto.subfooter",
        "collective.volto.formsupport",
    ],
    extras_require={
        "test": [
            "plone.app.testing",
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            "plone.testing>=5.0.0",
            "plone.app.contenttypes",
            "plone.app.robotframework[debug]",
            "collective.MockMailHost",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = iosanita.policy.locales.update:update_locale
    """,
)
