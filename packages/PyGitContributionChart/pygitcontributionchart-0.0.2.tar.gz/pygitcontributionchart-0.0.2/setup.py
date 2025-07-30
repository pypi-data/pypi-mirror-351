from setuptools import setup, find_packages

setup(
	name="PyGitContributionChart",
	version="0.0.2",
	packages=find_packages(),
	install_requires=[
		"pillow==10.2.0"
    ],
	long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
	description="A package for generating Git contribution charts",
	author="Sam Ramirez",
	url="https://github.com/arkangel-dev/GitCommitChart",
	classifiers=[
		"Programming Language :: Python :: 3"
	],
	python_requires=">=3.6",
)