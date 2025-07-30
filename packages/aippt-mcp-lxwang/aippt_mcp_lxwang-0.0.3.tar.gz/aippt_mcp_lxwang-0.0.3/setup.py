from setuptools import setup, find_packages

setup(
    name="aippt-mcp-lxwang",  # 包名（必须是唯一的）
    version="0.1.0",          # 版本号
    author="Your Name",       # 作者名
    author_email="your.email@example.com",  # 作者邮箱
    description="A short description of your package",  # 包描述
    long_description=open("README.md").read(),  # 长描述（通常从 README.md 读取）
    long_description_content_type="text/markdown",  # 长描述格式
    url="https://github.com/your_username/aippt-mcp-lxwang",  # 项目 URL
    packages=find_packages(),  # 自动查找包
    install_requires=[],       # 依赖包（可选）
    classifiers=[              # 分类信息（可选）
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",   # Python 版本要求
)
