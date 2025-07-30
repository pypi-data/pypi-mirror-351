from setuptools import setup, find_packages

setup(
    name="fundamint",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pandas",
        "transformers",
        "torch",
        "fastapi",
        "uvicorn",
        "pydantic",
        "newsapi-python",
        "yfinance",
    ],
    author="Paras Varshney",
    author_email="blurredmachine@gmail.com",
    description="A package for stock recommendations based on news analysis using LLMs",
    keywords="finance, stocks, news, llm, ai",
    url="https://github.com/blurred-machine/fundamint",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "fundamint=fundamint.cli:main",
        ],
    },
)