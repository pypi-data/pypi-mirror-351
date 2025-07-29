from setuptools import setup, find_packages

setup(
    name="bsmap",
    version="1.1.4",
    author="CodeSoftGit",
    description="Beat Saber Mapping Framework",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/CodeSoftGit/bsmap",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0", 
        "bstokenizer>=0.1.0",
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
