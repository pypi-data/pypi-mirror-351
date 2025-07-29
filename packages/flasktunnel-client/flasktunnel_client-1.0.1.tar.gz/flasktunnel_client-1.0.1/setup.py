# =============================================================================
# setup.py
# =============================================================================
#!/usr/bin/env python3
"""Setup script for FlaskTunnel Client."""

from setuptools import setup, find_packages
import os

# Read README.md for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="flasktunnel-client",
    version="1.0.1",
    author="Mohamed Ndiaye",
    author_email="mouhamedndiayegroupeisi@gmail.com",
    description="Client pour créer des tunnels HTTP sécurisés vers vos applications locales",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Moesthetics-code/flasktunnel-client.git",
    project_urls={
        "Bug Tracker": "https://github.com/Moesthetics-code/flasktunnel-client/issues",
        "Documentation": "https://docs.flasktunnel.dev",
        "Homepage": "https://flasktunnel.up.railway.app/",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Networking",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "flasktunnel=flasktunnel.cli:main",
        ],
    },
    keywords="tunnel, ngrok, flask, django, development, webhook, localhost, http, https",
    include_package_data=True,
    zip_safe=False,
)
