myproject/
├── setup.py              # 打包配置文件
├── README.md             # 项目说明
├── LICENSE               # 许可证文件
├── mypackage/            # 主模块目录
│   ├── __init__.py       # 模块初始化文件
│   └── module_file.py    # 代码文件
└── tests/                # 测试目录（可选）


使用说明
解压后，进入项目根目录（gethub_demo/）
# 升级 packaging
pip install -U packaging
安装打包工具：pip install build twine
生成包文件：python -m build
上传到 PyPI：python -m twine upload dist/*（需先注册 PyPI 账号）

PyPI 账号在 Windows 系统的命令提示符中，执行以下命令：
set TWINE_USERNAME=your_pypi_username
set TWINE_PASSWORD=your_pypi_password

PyPI 账号在 Linux 或 macOS 系统的终端中，执行以下命令：
export TWINE_USERNAME=your_pypi_username
export TWINE_PASSWORD=your_pypi_password

https://blog.csdn.net/QIDAL/article/details/148013142