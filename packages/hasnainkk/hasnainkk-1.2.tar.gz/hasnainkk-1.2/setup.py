from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hasnainkk",
    version="1.2",
    author="Endx0",
    author_email="lord_izana@yahoo.com",
    description="Hybrid Pyrogram + python-telegram-bot (PTB) Telegram Bot Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Endx0/hasnainkk",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pyrogram>=2.0.0",
        "python-telegram-bot>=20.0",
        "pyyaml>=6.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
        "Topic :: Communications :: Chat",
    ],
    python_requires=">=3.8",
)
