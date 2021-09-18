import re

from setuptools import find_packages, setup  # type: ignore

with open("valens/__init__.py", encoding="utf-8") as f:
    match = re.search(r'__version__ = "(.*?)"', f.read())
    assert match
    version = match.group(1)

setup(
    name="valens",
    version=version,
    license="AGPL-3.0",
    packages=find_packages(include=["valens"]),
    package_data={"valens": ["migrations/*", "migrations/versions/*"]},
    python_requires=">=3.8",
    install_requires=[
        "alembic >=1.6",
        "flask",
        "matplotlib",
        "pandas",
        "pyarrow",
        "sqlalchemy-repr >= 0.0.2",
        "sqlalchemy[mypy] >= 1.4",
    ],
    extras_require={
        "devel": [
            "black >=21.9b0",
            "flake8 >=3",
            "isort >=5",
            "mypy >=0.910",
            "pylint >=2.11.0",
            "pytest >=5",
            "pytest-alembic >=0.3.1",
            "pytest-cov >=2.10.0",
            "pytest-xdist >=1.32.0",
        ]
    },
    entry_points={"console_scripts": ["valens=valens.cli:main"]},
)
