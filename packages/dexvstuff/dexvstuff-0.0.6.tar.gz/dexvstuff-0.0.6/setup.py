from setuptools import setup, find_packages

setup(
    name="dexvstuff",
    version="0.0.6",
    author="Dexv",
    author_email="dexv@dexv.lol",
    description="Stuff i use in my projects",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dexvleads/dexvstuff",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "colorama",
        "requests",
        "javascript",
    ],
    python_requires=">=3.7",
)
