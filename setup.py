from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in jfs/__init__.py
from jfs import __version__ as version

setup(
	name="jfs",
	version=version,
	description="jfs",
	author="jfs",
	author_email="jfs@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
