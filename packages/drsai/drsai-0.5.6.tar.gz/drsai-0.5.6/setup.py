from setuptools import setup, find_packages
import os
import re

def parse_version_vars(pkg_path, filename="version.py"):
    """解析Python文件中的版本变量"""
    # 构建完整文件路径
    base_dir = os.path.abspath(os.path.dirname(__file__))
    version_path = os.path.join(base_dir, pkg_path, filename)
    
    # 支持多种赋值格式的正则模式
    pattern = re.compile(
        # r"^__(.*)?__*\s*=\s*['\"]([^'\"]*)['\"]",
        r"__(.*)?__.*?=(.*)",
        re.MULTILINE
    )

    try:
        with open(version_path, "r", encoding="utf-8") as f:
            return dict(pattern.findall(f.read()))
    except FileNotFoundError:
        print(f"Warning: {version_path} not found, using default values")
        return {}


version_info = parse_version_vars("drsai")
__version__ = eval(version_info.get("version", "0.0.1"))  # 支持带/不带__的变量名
__appname__ = eval(version_info.get("appname", "drsai"))
__author__ = eval(version_info.get("author", "Fitten Tech"))
__email__ = eval(version_info.get("email", "contact@fittentech.com"))
__description__ = eval(version_info.get("description", "A development framework for single and multi-agent collaborative systems developed by the Dr.Sai team at the IHEP, CAS."))


def get_requirements():
    with open('requirements.txt', encoding='utf-8') as f:
        return [
            line.strip()
            for line in f.readlines()
            if not line.startswith('#') and line.strip() != ''
        ]
    
setup(
    name=__appname__,  # 项目名称
    version=__version__,  # 版本号
    author=__author__,  # 作者信息
    author_email=__email__,  # 作者邮箱
    description=__description__,  # 项目描述
    long_description=open("README.md",encoding="utf-8").read(),  # 详细描述, 通常从README.md文件读取
    long_description_content_type="text/markdown",  # 描述的格式
    url="https://code.ihep.ac.cn/hepai/drsai/",  # 项目主页
    packages=find_packages(),  # 自动寻找项目中的包
    install_requires=get_requirements(),  # 依赖的包列表
    classifiers=[  # 分类标签，帮助用户找到你的项目
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',  # Python版本要求
    # entry_points={  # 可选的部分，用于创建命令行工具
    #     "console_scripts": [
    #         "your_command=your_module:main_function",
    #     ],
    # },
    include_package_data=True,  # 包含其它的非代码文件，比如数据文件
    package_data={  # 如果需要，可以在这里指定包含的文件类型
    },
)

# 将setup.py打包并上传到pypi
# python3 setup.py sdist bdist_wheel
# python3 -m twine upload dist/*
