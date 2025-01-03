from setuptools import setup, find_packages

setup(
    name="geminibpot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "discord.py>=2.3.2",
        "python-dotenv>=1.0.0",
        "google-generativeai>=0.3.0",
        "aiohttp>=3.8.0",
    ],
    author="ZeBookTech",
    author_email="contato@zebooktech.com",
    description="Bot Discord com integração Gemini AI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ZeBookTech/SamerPosterga",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)
