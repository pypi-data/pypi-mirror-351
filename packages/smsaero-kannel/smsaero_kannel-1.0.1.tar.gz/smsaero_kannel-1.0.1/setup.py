"""Setup script for the SmsAero Kannel client package."""

from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()


setup(
    name="smsaero_kannel",
    version="1.0.1",
    description="SMS Aero Kannel Lib",
    keywords=[
        "smsaero",
        "kannel",
        "sms",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="SmsAero",
    author_email="admin@smsaero.ru",
    maintainer="SmsAero Team",
    maintainer_email="support@smsaero.ru",
    url="https://github.com/smsaero/smsaero_python_kannel/",
    project_urls={
        "Homepage": "https://smsaero.ru/",
        "Repository": "https://github.com/smsaero/smsaero_python_kannel/",
        "Bug Tracker": "https://github.com/smsaero/smsaero_python_kannel/issues",
        "Help Center": "https://smsaero.ru/support/",
    },
    download_url="https://github.com/smsaero/smsaero_python_kannel/archive/refs/tags/1.0.1.tar.gz",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.6",
    include_package_data=True,
    install_requires=[
        "setuptools",
        "aiohttp>=3.9.1",
        "requests>=2.31.0",
        "phonenumbers>=8.13.40",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest >= 8.2.2",
            "flake8 >= 7.1.0",
            "ruff >= 0.4.10",
            "pylint >= 3.2.4",
            "tox >= 4.15.1",
            "mypy >= 1.10.0",
            "coverage >= 7.5.4",
            "bandit >= 1.7.9",
            "build >= 1.2.1",
            "twine >= 5.1.1",
        ],
    },
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Telephony",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    platforms=["any"],
    entry_points={
        "console_scripts": [
            "smsaero_kannel_send=smsaero_kannel.cmd_send:main",
        ],
    },
    options={
        "bdist_wheel": {"universal": True},
    },
)
