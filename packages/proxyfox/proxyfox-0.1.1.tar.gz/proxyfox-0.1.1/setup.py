from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="proxyfox",  # Use hyphen for pip install: pip install proxyfox
    version="0.1.1",
    author="Dev shetty",
    author_email="deviprasadshetty400@gmail.com",
    description="A simple Python package to fetch working proxies with filtering capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/redmoon0x/proxyfox",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
    ],
    keywords="proxy, proxies, proxy-list, proxy-server, proxy-checker",
    project_urls={
        "Bug Reports": "https://github.com/redmoon0x/proxyfox/issues",
        "Source": "https://github.com/redmoon0x/proxyfox",
    },
)
