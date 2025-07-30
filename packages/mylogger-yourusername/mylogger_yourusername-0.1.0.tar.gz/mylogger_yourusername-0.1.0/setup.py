from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mypa",
    version="0.1.0",
    author="wang lin",
    author_email="775290814@qq.com",
    description="stock L1",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/calculator_plus",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],  # 可以添加依赖项
)