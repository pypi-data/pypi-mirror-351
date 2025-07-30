from setuptools import find_packages, setup

setup(
    name="marketing_measures",
    version="0.1.0",
    author="Your Name",  # Please change this
    author_email="your.email@example.com",  # Please change this
    description="A Python package to score texts on marketing dimensions using Hugging Face transformers with optional ZCA transformation.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/marketing_measures",  # Please change this
    packages=find_packages(exclude=["examples"]),
    package_data={
        "marketing_measures": ["data/*.npz"],
    },
    install_requires=[
        "numpy",
        "pandas",
        "scipy",
        "transformers",
        "torch",
        "scikit-learn",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",  # Assuming MIT, can be changed
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing",
    ],
    python_requires=">=3.8",
)
