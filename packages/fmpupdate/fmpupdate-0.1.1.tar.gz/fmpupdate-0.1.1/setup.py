from setuptools import setup, find_packages


setup(
    name="fmpupdate",
    version="0.1.1",
    description="fmp tools",
    author="Hams",
    packages=find_packages(),
    install_requires=[
        "certifi==2025.4.26",
        "charset-normalizer==3.4.2",
        "idna==3.10",
        "numpy==2.2.6",
        "pandas==2.2.3",
        "python-dateutil==2.9.0.post0",
        "pytz==2025.2",
        "requests==2.32.3",
        "six==1.17.0",
        "tzdata==2025.2",
        "urllib3==2.4.0"
    ],
)