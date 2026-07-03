from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, comment='学生姓名')
    class_name = db.Column(db.String(20), comment='班级')
    scores = db.relationship('Score', backref='student', lazy=True, cascade='all, delete-orphan')
    #利用 SQLAlchemy 的 db.relationship 建立了双向关联，并用 backref 实现了反向查询
    #用 student.scores 直接拿到学生所有的成绩列表，有backref='student'，可以用 score.student 直接拿到这个成绩属于哪个学生。
    #cascade='all, delete-orphan',当删除 Student 对象时，所有关联的 Score 对象也会被自动删除
    def __repr__(self):
        return f'(Student {self.name})'

class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(30), nullable=False, comment='科目名称')
    value = db.Column(db.Float, nullable=False, comment='分数')
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    #外键，db.ForeignKey('students.id') 表示这一列引用的是 students 表里的 id
    __table_args__ = (db.UniqueConstraint('student_id', 'subject', name='_student_subject_uc'),)
    #数据库层级的“唯一性约束”，保障同一学生不能录入两门相同的科目

    def __repr__(self):
        return f'(Score {self.subject}: {self.value})'