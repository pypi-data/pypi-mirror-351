from setuptools import setup, find_packages


# Read the contents of README.md
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="appwrite-sync",
    version="0.4.5",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "appwrite_sync": ["templates/*.json", "templates/*.example"],
    },
    install_requires=["appwrite"],
    entry_points={
        "console_scripts": [
            "appwrite-sync=appwrite_sync.cli:main"
        ]
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Muhammad Yousif",
    author_email="aboidrees@gmail.com",
    description="A CLI tool to automate the creation and synchronization of Appwrite database collections from a JSON schema",
    url="https://github.com/aboidrees/appwrite-sync",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.9",
)
