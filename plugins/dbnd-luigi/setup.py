from os import path

import setuptools

from setuptools.config import read_configuration


BASE_PATH = path.dirname(__file__)
CFG_PATH = path.join(BASE_PATH, "setup.cfg")

config = read_configuration(CFG_PATH)
version = config["metadata"]["version"]

setuptools.setup(
    name="dbnd-luigi",
    package_dir={"": "src"},
    install_requires=["dbnd==" + version, "luigi"],
    entry_points={
        "console_scripts": ["dbnd-luigi = dbnd_luigi.luigi_tracking:dbnd_luigi_run",],
    },
)
