import setuptools
with open('README.md', 'r', encoding='utf-8') as fh:
	long_description = fh.read()

setuptools.setup(
	name='weatherapibyAli',
	version='9.0.0',
	author='__init__',
	author_email='jamshidkushbaev@gmail.com',
	description='Это Проект Weather App. This Project Weather App.',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://github.com/alikushbaev/Weatherapp',
	project_urls={
		'Documentation': 'https://github.com/alikushbaev/Weatherapp',
	},
	packages=['WeatherapibyAli'],
	install_requires=["requests", "datetime", "pystray", "pytz", "geopy", "pillow", "timezonefinder"],
	include_package_data=True,
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	python_requires='>=3.11',
)