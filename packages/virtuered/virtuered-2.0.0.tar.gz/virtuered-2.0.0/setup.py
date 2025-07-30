from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requirements = [
    "requests>=2.25.1",
    "rich>=10.0.0",
    "flask>=2.0.0",
    "flask-cors>=3.0.0",
    "waitress>=2.0.0",
    "pyyaml>=6.0.0",
    # --- Add dependencies from webui ---
    "fastapi>=0.70.0", 
    "uvicorn[standard]>=0.15.0", 
    "click>=7.0", 
    "pyfiglet>=0.8" 
]

setup(
    name="virtuered",
    version="2.0.0",
    author="Virtue AI",
    author_email="yijiazheng@virtueai.com",
    license="MIT",
    description="CLI tool and Model Server for VirtueAI VirtueRed",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Virtue-AI/VirtueRed-CLI.git",
    packages=find_packages(),
    # --- Include package data (frontend files) ---
    include_package_data=True, 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'virtuered=virtuered.cli.commands:main',
        ],
    },
)