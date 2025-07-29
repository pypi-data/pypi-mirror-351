from setuptools import setup, find_packages

setup(
    name="chronodeck",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Chronodeck",
    packages=find_packages(),
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "chronodeck=chronodeck:main",
        ],
    },
)
