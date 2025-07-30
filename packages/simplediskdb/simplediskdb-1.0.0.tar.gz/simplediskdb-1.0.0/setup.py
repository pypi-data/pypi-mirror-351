from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="simplediskdb",
    version="1.0.0",
    author="Anandan B S",
    author_email="anandanklnce@gmail.com",
    description="A MongoDB-style disk-based database implementation, persistent storage for python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anandan-bs/simplediskdb",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=[
        "diskcache>=5.0.0",
        "flask>=2.0.0",
    ],
    entry_points={
        'console_scripts': [
            'simplediskdb=simplediskdb.cli:main',
        ],
    },
    package_data={
        'simplediskdb': ['templates/*'],
    },
    include_package_data=True,
)
