from app import app
from models import db

# 在应用上下文内创建所有表
with app.app_context():
    db.create_all()
    print("数据库 grades.db 创建成功")
    print("已创建表:students(学生表)、scores(成绩表)")