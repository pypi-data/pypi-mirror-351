import os
import setuptools

if os.environ.get('CI_COMMIT_TAG'):
    version = os.environ['CI_COMMIT_TAG']
elif os.environ.get('CI_JOB_ID'):
    version = os.environ['CI_JOB_ID']
else:
    version = None

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

packages = setuptools.find_packages(
    where='.',
    exclude=['tests*'],
)

setuptools.setup(
    name="sentinelc-appfeed",
    version=version,
    url="https://gitlab.com/sentinelc/app-library-builder",
    maintainer="SentinelC",
    description="Tools used to validate, create and publish an app libary feed for the SentinelC platform.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=packages,
    entry_points={
        "console_scripts": [
            "applib-builder = sentinelc_appfeed.builder:main",
            "applib-validator = sentinelc_appfeed.validator:main",
        ]
    },
    install_requires=[
        "PyYAML",
        "humanfriendly",
        "jinja2",
    ],
    include_package_data=True,
)
