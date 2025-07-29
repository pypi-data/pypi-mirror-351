from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="peer2peerchat",
    version="0.2.2",
    author="No Name",
    description="A simple peer-to-peer chat application with clipboard sharing functionality",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abdullah134/p2pchat",
    packages=["peer2peer"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Communications :: Chat",
        "Topic :: Internet",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pyperclip"
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "p2pchat=peer2peer:Peer",
        ],
    },
)