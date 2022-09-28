import sys

from setuptools import find_packages, setup


def get_version(filename):
    import ast

    version = None
    with open(filename) as f:
        for line in f:
            if line.startswith("__version__"):
                version = ast.parse(line).body[0].value.s
                break
        else:
            raise ValueError("No version found in %r." % filename)
    if version is None:
        raise ValueError(filename)
    return version


version = get_version(filename="src/imitation-fuzzing/__init__.py")

install_requires = [
    "gym>=0.17.1",
    "numpy>=1.10.0",
]

system_version = tuple(sys.version_info)[:3]

if system_version < (3, 7):
    install_requires.append("dataclasses")

setup(
    name=f"imitation_fuzzing",
    package_dir={"": "src"},
    packages=find_packages("src"),
    zip_safe=False,
    version=version,
    keywords="rl, openaigym, openai-gym, gym",
    include_package_data=True,
    install_requires=install_requires,
)
