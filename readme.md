# 学生成绩管理系统
一个基于 Flask + SQLAlchemy 的极简学生成绩管理工具，支持学生信息录入、成绩录入与修改、按学生查看成绩列表。

# 特点
学生管理：添加、查看、删除学生
成绩管理：录入、修改、删除成绩
成绩统计：自动计算每个学生的总分和平均分
数据回显：表单提交失败时自动保留已填内容
级联删除：删除学生时自动删除其所有成绩

# 技术栈
Python 3.11+
Flask
Flask-SQLAlchemy
SQLite3
Bootstrap 5
Jinja2 模板

# 创建并激活虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python init_db.py

# 启动项目
python app.py
浏览器访问 `http://127.0.0.1:5001`