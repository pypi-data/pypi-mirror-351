# 开发模式安装：pip install -e .
# rm -rf build dist *.egg-info & python setup.py sdist bdist_wheel
# python -m twine upload dist/*
# pip install -U ragxis -i https://pypi.org/simple/

from setuptools import setup, find_packages
from ragxis import __version__
setup(
    name="ragxis",
    version=__version__,
    packages=find_packages(),
    install_requires=[
        # 你可以这里写依赖，比如 "torch", "transformers" 等
    ],
    python_requires='>=3.10',
)
