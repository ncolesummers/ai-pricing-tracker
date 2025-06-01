from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-pricing-tracker",
    version="0.1.0",
    author="Cole Summers",
    author_email="your.email@example.com",
    description="Auto-updating AI API pricing data for Claude, OpenAI, and more",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/colesummers/ai-pricing-tracker",
    project_urls={
        "Bug Tracker": "https://github.com/colesummers/ai-pricing-tracker/issues",
        "Documentation": "https://github.com/colesummers/ai-pricing-tracker#readme",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.990",
            "build>=0.7.0",
            "twine>=4.0.0",
        ],
        "scraper": [
            "playwright>=1.30.0",
            "beautifulsoup4>=4.11.0",
        ],
    },
    package_data={
        "ai_pricing_tracker": ["data/*.json"],
    },
    entry_points={
        "console_scripts": [
            "ai-pricing-update=ai_pricing_tracker.cli:main",
        ],
    },
)
