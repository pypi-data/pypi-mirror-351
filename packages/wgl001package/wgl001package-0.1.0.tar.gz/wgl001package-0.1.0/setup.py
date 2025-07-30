from setuptools import setup, find_packages

# 打开 README.md 文件时指定编码为 UTF-8
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="wgl001package",               # PyPI 上的包名
    version="0.1.0",                # 版本号
    author="Your Name",
    author_email="your@email.com",
    description="A short description",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/myproject",
    packages=find_packages(),       # 自动发现所有模块
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",         # 最低 Python 版本要求
    install_requires=[              # 依赖列表
        "requests>=2.25.1",
    ],
    license="MIT",  # 指定许可证类型
)