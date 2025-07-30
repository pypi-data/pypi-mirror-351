"""
Setup script for YFRLT - Yahoo Finance Real-Time
"""

from setuptools import setup, find_packages

# Read README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="yfrlt",
    version="1.0.0",
    author="ijuice-20",
    author_email="ijasahammedj@gmail.com", 
    description="Yahoo Finance Real-Time WebSocket Library for streaming live market data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ijuice-20/yfrlt",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry", 
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "websocket-client>=1.6.0",
        "websockets>=11.0.0",
    ],
    keywords=[
        "yahoo", "finance", "websocket", "realtime", "stocks", "crypto", 
        "trading", "market-data", "financial-data", "streaming"
    ],
)