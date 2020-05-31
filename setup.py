from setuptools import setup
import os

setup(
    use_scm_version={
        "version_scheme": os.getenv("SCM_VERSION_SCHEME", "guess-next-dev"),
        "local_scheme": os.getenv("SCM_LOCAL_SCHEME", "node-and-date"),
    },
)
