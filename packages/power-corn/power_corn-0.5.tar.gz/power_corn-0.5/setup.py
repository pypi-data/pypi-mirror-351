from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="power_corn",
    version="0.5",
    packages=find_packages(),
    install_requires=["supabase"],
    entry_points={
        "console_scripts": ["power_corn = src.main:main"],
    },
    long_description=description,
    long_description_content_type="text/markdown",
)
