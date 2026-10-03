import os

from flask import Flask, flash, redirect, render_template, request, url_for

from models import Score, Student, db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grades.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭追踪
# 会话加密密钥：生产环境请用环境变量 SECRET_KEY 覆盖默认值
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')

db.init_app(app)


def parse_score_form():
    """读取并校验成绩表单，返回 (subject, value, error)。

    校验通过时 error 为 None，value 是 float；否则 value 保留表单里的原始字符串，
    交给模板原样回显，避免用户重复输入。
    """
    subject = (request.form.get('subject') or '').strip()
    raw_value = request.form.get('value')
    if not subject or raw_value in (None, ''):
        return subject, raw_value, '科目和分数都不能为空！'
    try:
        return subject, float(raw_value), None
    except (TypeError, ValueError):
        return subject, raw_value, '分数必须是数字！'


@app.template_filter('number')
def format_number(value):
    """去掉多余的尾随 0，避免出现 90.0 / 183.50000000000003 这类展示。"""
    text = f'{float(value):.10f}'.rstrip('0').rstrip('.')
    return text if text not in ('', '-0') else '0'


@app.route('/')
def index():
    # 相当于 SQL 的 SELECT * FROM students ORDER BY id DESC
    students = Student.query.order_by(Student.id.desc()).all()
    return render_template('index.html', students=students)


@app.route('/student/<int:student_id>')
def student_detail(student_id):
    # 根据 ID 查学生，如果不存在直接返回 404 页面
    student = db.get_or_404(Student, student_id)
    return render_template(
        'student_detail.html',
        student=student,
        scores=student.scores,
        total=student.total_score,
        average=student.average_score,
    )


@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = (request.form.get('name') or '').strip()
        class_name = (request.form.get('class_name') or '').strip() or None
        if not name:
            flash('学生姓名不能为空！', 'danger')
            return render_template('add_student.html')

        new_student = Student(name=name, class_name=class_name)
        db.session.add(new_student)  # 将新学生对象添加到数据库的“待提交队列”中
        db.session.commit()          # 真正执行提交，将数据写入 grades.db 文件
        flash(f'学生 {name} 添加成功！', 'success')
        return redirect(url_for('index'))

    return render_template('add_student.html')


@app.route('/score/add/<int:student_id>', methods=['GET', 'POST'])
def add_score(student_id):
    # 根据 ID 查学生，如果不存在直接返回 404 页面
    student = db.get_or_404(Student, student_id)
    if request.method == 'POST':
        subject, value, error = parse_score_form()
        if error:
            flash(error, 'danger')
            return render_template('add_score.html', student=student)

        existing = Score.query.filter_by(student_id=student_id, subject=subject).first()
        if existing:
            flash(f'该学生已有 {subject} 成绩！', 'warning')
            return render_template('add_score.html', student=student)

        db.session.add(Score(student_id=student_id, subject=subject, value=value))
        db.session.commit()
        flash(f'成功录入 {subject} 成绩：{value:g} 分', 'success')
        return redirect(url_for('student_detail', student_id=student_id))

    return render_template('add_score.html', student=student)


@app.route('/score/edit/<int:score_id>', methods=['GET', 'POST'])
def edit_score(score_id):
    score = db.get_or_404(Score, score_id)
    student = score.student

    if request.method == 'POST':
        subject, value, error = parse_score_form()
        if error:
            flash(error, 'danger')
            return render_template('edit_score.html', score=score, student=student)

        # 同一学生下，除当前这条记录外不允许出现重复科目
        duplicated = Score.query.filter(
            Score.student_id == student.id,
            Score.subject == subject,
            Score.id != score_id,
        ).first()
        if duplicated:
            flash(f'该学生已有 {subject} 成绩！', 'warning')
            return render_template('edit_score.html', score=score, student=student)

        score.subject = subject
        score.value = value
        db.session.commit()
        flash(f'成绩已更新为 {subject}：{value:g} 分', 'success')
        return redirect(url_for('student_detail', student_id=student.id))

    return render_template('edit_score.html', score=score, student=student)


@app.route('/score/delete/<int:score_id>', methods=['POST'])
def delete_score(score_id):
    score = db.get_or_404(Score, score_id)
    student_id = score.student_id
    subject = score.subject  # 先取出内容，避免删除后对象处于失效状态
    db.session.delete(score)
    db.session.commit()
    flash(f'已删除 {subject} 成绩', 'success')
    return redirect(url_for('student_detail', student_id=student_id))


@app.route('/student/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    student = db.get_or_404(Student, student_id)
    name = student.name
    db.session.delete(student)
    db.session.commit()
    flash(f'学生 "{name}" 及其所有成绩已删除', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=5001)
