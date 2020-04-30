import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="betfairstreamer",
    version="0.6.0",
    author="Jonatan Almen",
    zip_safe=False,
    author_email="almen.jonatan@gmail.com",
    description="Betfair Exchange Stream API wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/almenjonatan/betfairstreamer.git",
    packages=["betfairstreamer", "betfairstreamer.models", "betfairstreamer.stream"],
    package_data={"betfairstreamer": ["py.typed"]},
    install_requires=[
        "betfairlightweight",
        "orjson",
        "numpy",
        "ciso8601",
        "attrs",
        "pytz",
        "zmq"
    ],
    include_package_data=True,
    entry_points={"console_scripts": ["betfairstreamer = betfairstreamer.server:start"]},
    classifiers=["Programming Language :: Python :: 3", "License :: OSI Approved :: MIT License"],
    python_requires=">=3.8.0",
)
