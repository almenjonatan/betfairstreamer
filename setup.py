import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="betfairstreamer",  # Replace with your own username
    version="0.2.2",
    author="Jonatan Almen",
    author_email="almen.jonatan@gmail.com",
    description="Server for Exchange Stream API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/almenjonatan/betfairstreamer.git",
    packages=setuptools.find_packages(),
    install_requires=[
        "betfairlightweight",
        "orjson",
        "numpy",
        "pyzmq",
        "ciso8601",
        "attrs",
        "pytz",
    ],
    entry_points={
        "console_scripts": ["betfairstreamer = betfairstreamer.server:start",],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8.0",
)
