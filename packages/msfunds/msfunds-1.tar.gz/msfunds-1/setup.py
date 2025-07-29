from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="msfunds",
    version="1",
    packages=find_packages(),
    package_data={
        "msfunds.Utils": ["*.json"],
    },
    include_package_data=True,
    description="Fetches Funds data from Morningstar.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="nndjoli",
    url="https://github.com/nndjoli/morningstar-funds-data-fetcher",
    install_requires=[
        "pandas",
        "ua_generator",
        "httpx",
        "beautifulsoup4",
        "nest_asyncio",
        'importlib_resources; python_version<"3.9"',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
