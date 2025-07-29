from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="loggier",
    version="0.1.7",
    author="Yigit ALTINTAS",
    author_email="'yigit.altintas@loggier.app",
    description="Python tabanlı backend uygulamaları için log yönetim kütüphanesi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yigitaltintas/loggier",
    project_urls={
        "Bug Tracker": "https://github.com/yigitaltintas/loggier/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging",
    ],
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
        "tqdm>=4.61.0",
        "psutil>=5.8.0",
    ],
    keywords="logging, error tracking, monitoring, backend, api",
)