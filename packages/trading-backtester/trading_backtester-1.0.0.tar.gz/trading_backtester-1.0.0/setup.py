from setuptools import setup

setup(
    name="trading-backtester",
    version="1.0.0",
    description="A trading backtesting framework for Python",
    url="https://github.com/madamskip1/trading-backtester",
    project_urls={
        "Source": "https://github.com/madamskip1/trading-backtester",
    },
    author="Adamski Maciej",
    author_email="madamskip1@gmail.com",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=["trading_backtester"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    license="MIT",
    python_requires=">=3.6",
    install_requires=[
        "numpy>=1.16.0",
        "matplotlib>=3.0.0",
    ],
)
