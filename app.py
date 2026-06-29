from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Student,Score

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grades.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭追踪
app.secret_key = 'hello'

db.init_app(app)

@app.route('/')
def index():
    students = Student.query.order_by(Student.id.desc()).all()
    #SQLAlchemy 的查询语法。相当于 SQL 的 SELECT * FROM students ORDER BY id DESC
    #从数据库查询所有学生，按 id 降序排列
    return render_template('index.html', students=students)

@app.route('/student/<int:student_id>')
def student_detail(student_id):
    student = Student.query.get_or_404(student_id)
    scores = student.scores
    total = sum(score.value for score in scores)
    average = total / len(scores) if scores else 0  # 避免除以 0 错误
    
    return render_template(
        'student_detail.html',
        student=student,
        scores=scores,
        total=total,
        average=average
    )

@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form.get('name')
        class_name = request.form.get('class_name')
        if not name:
            flash('学生姓名不能为空！', 'danger')
            return render_template('add_student.html', name=name, class_name=class_name)
        new_student = Student(name=name, class_name=class_name)
        db.session.add(new_student)  #将新学生对象添加到数据库的“待提交队列”中
        db.session.commit()          #真正执行提交，将数据写入 grades.db 文件
        
        flash(f'学生 {name} 添加成功！', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_student.html')

@app.route('/score/add/<int:student_id>', methods=['GET', 'POST'])
def add_score(student_id):
    student = Student.query.get_or_404(student_id)
    #根据 ID 查学生，如果不存在直接返回 404 页面
    if request.method == 'POST':
        subject = request.form.get('subject')
        value = request.form.get('value')
        if not subject or not value:
            flash('科目和分数都不能为空！', 'danger')
            return render_template('add_score.html', student=student, subject=subject, value=request.form.get('value'))
        try:
            value = float(value)  # 转成浮点数
        except ValueError:
            flash('分数必须是数字！', 'danger')
            return render_template('add_score.html', student=student, subject=subject, value=request.form.get('value'))
        existing = Score.query.filter_by(student_id=student_id, subject=subject).first()
        if existing:
            flash(f'该学生已有 {subject} 成绩！', 'warning')
            return render_template('add_score.html', student=student, subject=subject, value=request.form.get('value'))
        new_score = Score(student_id=student_id, subject=subject, value=value)
        db.session.add(new_score)
        db.session.commit()
        flash(f'成功录入 {subject} 成绩：{value} 分', 'success')
        return redirect(url_for('student_detail', student_id=student_id))
    return render_template('add_score.html', student=student)

@app.route('/score/edit/<int:score_id>', methods=['GET', 'POST'])
def edit_score(score_id):
    score = Score.query.get_or_404(score_id)
    student = score.student
    
    if request.method == 'POST':
        subject = request.form.get('subject')
        value = request.form.get('value')
        if not subject or not value:
            flash('科目和分数都不能为空！', 'danger')
            return render_template('edit_score.html', score=score, student=student)
        
        try:
            value = float(value)
        except ValueError:
            flash('分数必须是数字！', 'danger')
            return render_template('edit_score.html', score=score, student=student)
        existing = Score.query.filter(
            Score.student_id == student.id,
            Score.subject == subject,
            Score.id != score_id
        ).first()
        if existing:
            flash(f'该学生已有 {subject} 成绩！', 'warning')
            return render_template('edit_score.html', score=score, student=student)
        score.subject = subject
        score.value = value
        db.session.commit()
        flash(f'成绩已更新为 {subject}:{value} 分', 'success')
        return redirect(url_for('student_detail', student_id=student.id))
    return render_template('edit_score.html', score=score, student=student)

@app.route('/score/delete/<int:score_id>', methods=['POST'])
def delete_score(score_id):
    score = Score.query.get_or_404(score_id)
    student_id = score.student_id
    db.session.delete(score)
    db.session.commit()
    flash(f'已删除 {score.subject} 成绩', 'success')
    return redirect(url_for('student_detail', student_id=student_id))

@app.route('/student/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    name = student.name
    db.session.delete(student)
    db.session.commit()
    flash(f'学生 "{name}" 及其所有成绩已删除', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)