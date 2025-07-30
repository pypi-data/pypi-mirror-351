import setuptools

setuptools.setup(
	name="tp_http_request_response_parser",
	version="2025.5.30",
	author="TP Cyber Security",
	license="MIT",
	author_email="tpcybersec2023@gmail.com",
	description="Parse/ Unparse the HTTP Request/ Response",
	long_description=open("README.md").read(),
	long_description_content_type="text/markdown",
	install_requires=open("requirements.txt").read().split(),
	url="https://github.com/tpcybersec/TP-HTTP-Request-Response-Parser",
	classifiers=[
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 2",
		"Programming Language :: Python :: Implementation :: Jython"
	],
	keywords=["TPCyberSec", "HTTP Request Parser", "HTTP Response Parser"],
	packages=setuptools.find_packages(),
)