from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, comment='学生姓名')
    class_name = db.Column(db.String(20), comment='班级')

    # db.relationship 建立一对多双向关联：
    #   student.scores 直接拿到该学生的所有成绩；
    #   backref='student' 让 score.student 反查所属学生；
    #   cascade='all, delete-orphan' 删除学生时级联删除其成绩；
    #   order_by 让成绩按主键稳定输出，避免每次展示顺序不一致。
    scores = db.relationship(
        'Score',
        backref='student',
        lazy=True,
        cascade='all, delete-orphan',
        order_by='Score.id',
    )

    @property
    def total_score(self):
        """总分：没有成绩时返回 0。"""
        return sum(score.value for score in self.scores)

    @property
    def average_score(self):
        """平均分：没有成绩时返回 0，避免除以 0 错误。"""
        if not self.scores:
            return 0
        return self.total_score / len(self.scores)

    def __repr__(self):
        return f'<Student {self.id} {self.name}>'


class Score(db.Model):
    __tablename__ = 'scores'

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(30), nullable=False, comment='科目名称')
    value = db.Column(db.Float, nullable=False, comment='分数')

    # 外键，db.ForeignKey('students.id') 表示这一列引用 students 表里的 id
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)

    # 数据库层级的唯一性约束：保障同一学生不能录入两门相同科目
    __table_args__ = (db.UniqueConstraint('student_id', 'subject', name='_student_subject_uc'),)

    def __repr__(self):
        return f'<Score {self.subject}: {self.value}>'
