# UtilsZ
Python common utils

## 使用说明

                                                                       
## 项目说明
### 目录说明
- README.md: 包含使用手册、项目说明

### 执行依赖安装
pip install -r requirements.txt

### 依赖固化
pip freeze > requirements.txt

### 打包
1. pip install build
2. python -m build

### 发布到pypi
1. pip install twine  
2. python -m twine upload --repository pypi dist/*
3. 输入用户名和API Token。