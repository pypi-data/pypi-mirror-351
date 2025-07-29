from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lm-raindrop-integrations",
    version="0.1.5",
    author="LiquidMetal",
    author_email="customer@liquidmetal.ai",
    description="Python SDK for Integrations with LiquidMetal products",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/liquidmetal-ai/lm-raindrop-integrations",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
) 