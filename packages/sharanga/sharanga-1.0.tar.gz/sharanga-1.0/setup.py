from setuptools import setup, find_packages

setup(
    name='sharanga',
    version='1.0',
    description="Sharanga is a fast, asynchronous port scanner written in Python. It supports domain/IP/CIDR scanning, custom ports, banner grabbing, and service detection. Ideal for recon, pentesting, and network analysis.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Eshan Singh",
    author_email="r0x4r@yahoo.com",
    url="https://github.com/R0X4R/sharanga",
    license="MIT",
    packages=find_packages(),
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'sharanga = sharanga.scanner:cli',
        ],
    },
    classifiers = [
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Security",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: Utilities"
]
)
