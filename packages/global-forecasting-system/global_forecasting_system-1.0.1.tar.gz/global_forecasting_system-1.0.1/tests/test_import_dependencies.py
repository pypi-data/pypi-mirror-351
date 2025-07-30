import pytest

# List of dependencies
dependencies = [
    "bs4",
    "colored_logging",
    "dateutil",
    "matplotlib",
    "numpy",
    "pandas",
    "pygrib",
    "rasters",
    "requests"
]

# Generate individual test functions for each dependency
@pytest.mark.parametrize("dependency", dependencies)
def test_dependency_import(dependency):
    __import__(dependency)
