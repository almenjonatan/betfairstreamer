import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="betfairstreamer",
    version="0.4.0",
    author="Jonatan Almen",
    zip_safe=False,
    author_email="almen.jonatan@gmail.com",
    description="Server for Exchange Stream API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/almenjonatan/betfairstreamer.git",
    packages=["betfairstreamer", "betfairstreamer.betfair", "betfairstreamer.cache", "betfairstreamer.utils"],
    package_data={"betfairstreamer": ["py.typed"]},
    install_requires=[
        "betfairlightweight",
        "orjson",
        "numpy",
        "pyzmq",
        "ciso8601",
        "attrs",
        "pytz",
    ],
    include_package_data=True,
    entry_points={"console_scripts": ["betfairstreamer = betfairstreamer.server:start"]},
    classifiers=["Programming Language :: Python :: 3", "License :: OSI Approved :: MIT License"],
    python_requires=">=3.8.0",
)
