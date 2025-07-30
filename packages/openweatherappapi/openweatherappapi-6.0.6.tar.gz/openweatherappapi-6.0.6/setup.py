import setuptools
with open('README.md', 'r', encoding='utf-8') as fh:
	long_description = fh.read()

setuptools.setup(
	name='openweatherappapi',
	version='6.0.6',
	author='__token__',
	author_email='jamshidkushbaev@gmail.com',
	description='openweatherappapi',
	long_description=long_description,
	long_description_content_type='text/markdown',
	packages=['openweatherappapi'],
	install_requires=["pytz", "datetime", "timezonefinder", "requests", "pillow", "pystray", "geopy"],
	include_package_data=True,
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.11',
)