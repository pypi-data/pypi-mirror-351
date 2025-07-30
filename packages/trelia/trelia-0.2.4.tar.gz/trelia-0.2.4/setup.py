from setuptools import setup, find_packages

setup(
    name="trelia",
    version="0.2.4",
    description="A Python package to rate and review student code using the Gemini API",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Aegletek",
    author_email="coe@aegletek.com",
    url="https://www.aegletek.com/",
    license="MIT",
    packages=find_packages(),  # auto-detects 'trelia' directory
    include_package_data=True,  # include files from MANIFEST.in
    install_requires=[
        "google-generativeai",
        "langchain",  # if you're using LangChain for prompt templates
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
    ],
    python_requires=">=3.7",
)
