"""
iTechSmart Supreme - Setup Script
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="itechsmart-supreme",
    version="1.0.0",
    author="iTechSmart Inc.",
    author_email="support@itechsmart.dev",
    description="Autonomous AI agent for real-time infrastructure issue detection and resolution",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/itechsmart-supreme",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "itechsmart-supreme=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "itechsmart_supreme": [
            "web/templates/*.html",
            "web/static/css/*.css",
            "web/static/js/*.js",
        ],
    },
)