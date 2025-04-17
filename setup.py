#!/usr/bin/env python3

from setuptools import setup

setup(
    name="ai-tools",
    version="0.1.0",
    description="AI Tools with Ollama LLM integration for OS assistance",
    # This allows setup.py to defer to pyproject.toml for package configuration
    setup_requires=["poetry-core>=1.0.0"],
    install_requires=[],  # Poetry will handle the dependencies
    python_requires=">=3.10",
)