
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="smartagent-sf",
    version="0.1.3",
    author="Liedson Habacuc",
    author_email="lisvaldosf@gmail.com",
    license="MIT",
    description="Biblioteca Python para criar agentes de IA com execução determinística",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lhabacuc/smartagent",
    packages=find_packages(include=["agent", "agent.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        'dev': [
            'groq',
            'openai',
            'google-generativeai',
            'ollama',
            'llama-cpp-python',
            'pytest',
            'pytest-mock',
            'black',
            'flake8',
            'mypy',
            'isort',
            'requests'
        ],
    },
)
