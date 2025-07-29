from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="py-dnscheck",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "dnspython"
    ],
    author="Santhosh Murugesan",
    author_email="santhoshm.murugesan@gmail.com",
    description="A Python module to perform DNS resolution, health check and configuration.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows"
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'dnscheck=dnscheck.cli:main',
        ],
    },
)
