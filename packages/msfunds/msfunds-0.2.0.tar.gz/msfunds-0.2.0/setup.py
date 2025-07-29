from setuptools import setup, find_packages

# Lire le contenu de README.md pour la description longue
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="msfunds",  # Nom de votre package
    version="0.2.0",  # Version initiale
    packages=find_packages(),
    description="Fetches Funds data from Morningstar.",  # Adaptez
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="nndjoli",  # Adaptez
    url="https://github.com/nndjoli/morningstar-funds-data-fetcher",  # Adaptez
    install_requires=[
        "pandas",
        "ua_generator",
        "httpx",
        "beautifulsoup4",
        "nest_asyncio",
        'importlib_resources; python_version<"3.9"',
    ],
    package_data={
        "msfunds": ["Utils/*.json"],  # Modification ici
    },
    include_package_data=True,  # Ajout de cette ligne
    classifiers=[  # Recommandé : aide les utilisateurs à trouver votre package
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Choisissez votre licence
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",  # Spécifiez les versions de Python supportées
)
