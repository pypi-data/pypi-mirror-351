from setuptools import setup, find_packages

setup(
    name="xyz-tools-plus",
    version="0.2.1-beta1",
    author="mly, wyy, sty",
    description="一个用于多功能的Python库",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
    include_package_data=True,
    install_requires=[
        "numpy"
    ],  
)