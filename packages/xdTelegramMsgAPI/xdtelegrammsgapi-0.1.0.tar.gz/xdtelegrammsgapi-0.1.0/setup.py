from setuptools import setup, find_packages

setup(
    name="xdTelegramMsgAPI",
    version="0.1.0",
    author="Ayush Biswas",
    author_email="adgaming780@gmail.com",
    description="A Python library for sending messages via the xd-org.site Telegram API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ayushbiswas007/xdTelegramMsgAPI",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
