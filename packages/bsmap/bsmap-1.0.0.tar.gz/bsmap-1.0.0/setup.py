from setuptools import setup, find_packages

setup(
    name="bsmap",
    version="1.0.0",
    author="CodeSoftGit",
    description="Beat Saber Mapping Framework",
    long_description="A comprehensive framework for creating, editing, and validating Beat Saber maps.",
    url="https://github.com/CodeSoftGit/bsmap",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0", 
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Games/Entertainment",
    ],
    python_requires='>=3.8'
)