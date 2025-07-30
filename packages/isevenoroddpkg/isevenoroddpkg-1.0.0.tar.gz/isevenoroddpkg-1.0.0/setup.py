from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='isevenoroddpkg',
    version='1.0.0',
    description="Number validator",
    long_description=long_description,
    author="Parmeshwar",
    author_email="parmeshwar@mindkosh.com",
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.7',
    install_requires=[
        "validators==0.20.0"
    ],
    keywords=["even-odd-validator"],
)
