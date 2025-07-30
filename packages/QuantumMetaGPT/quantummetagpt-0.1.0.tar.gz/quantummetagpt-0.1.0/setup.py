from setuptools import setup, find_packages

setup(
    name="QuantumMetaGPT",
    version="0.1.0",
    description="Autonomous quantum AI research agent",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Quantum Research Team",
    packages=find_packages(),
    install_requires=[
        "qiskit>=0.44",
        "qiskit-ibmq-provider",
        "stable-baselines3",
        "arxiv",
        "openai",
        "transformers",
        "torch",
        "matplotlib",
        "pylatex",
        "cryptography",
        "fastapi",
        "uvicorn",
        "python-dotenv",
        "gym"
    ],
    entry_points={
        "console_scripts": [
            "qmetagpt = main:main",
            "qmetagpt-license = qmetagpt.security_licensing.cli_license:cli"
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.10",
    ],
)