from setuptools import setup, find_packages

setup(
    name="aippt-mcp-fix",  # 包名（必须是唯一的）
    version="0.0.6",          # 版本号
    author="lxwang",       # 作者名
    author_email="2418864969@qq.com",  # 作者邮箱
    description="A short description of your package",  # 包描述
    long_description=open("README.md").read(),  # 长描述（通常从 README.md 读取）
    long_description_content_type="text/markdown",  # 长描述格式
    url="https://github.com/Alex-Smith-1234/aippt-mcp-lxwang.git",  # 项目 URL
    packages=find_packages(),  # 自动查找包
    install_requires = [
        "mcp[cli]>=1.3.0",
        "requests",
        "requests_toolbelt"
    ],
    python_requires=">=3.10",   # Python 版本要求
)
