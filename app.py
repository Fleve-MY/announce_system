from flask import Flask, render_template, request, session, redirect, url_for, flash
import pymysql
import hashlib
import os
import secrets # 引入 secrets 模块

app = Flask(__name__)

# --- MySQL 数据库配置 ---
db_config = {
    'host': 'rm-uf676t3tz1ixx3yl92o.mysql.rds.aliyuncs.com',
    'port': 2558,
    'user': 'fyj',
    'password': 'fyj@12345',
    'database': 'announce_system',
    'cursorclass': pymysql.cursors.DictCursor
}

# 持久化Secret Key
def get_or_create_secret_key(key_file='secret.key'):

    if os.path.exists(key_file):
        with open(key_file, 'r') as f:
            key = f.read().strip()
            print(f"从 {key_file} 文件中加载了已存在的 Secret Key。")
            return key
    else:
        new_key = secrets.token_hex(24) # 十六进制
        with open(key_file, 'w') as f:
            f.write(new_key)
        print(f"生成了新的 Secret Key 并保存到 {key_file} 文件中。")
        return new_key

# 设置 Secret Key
app.secret_key = get_or_create_secret_key()


# 数据库连接辅助
def get_db_connection():
    try:
        conn = pymysql.connect(**db_config)
        return conn
    except pymysql.Error as e:
        print(f"数据库连接失败: {e}")
        return None


# 数据库初始化
def init_db():
    temp_config = db_config.copy()
    temp_config.pop('cursorclass', None)
    conn = pymysql.connect(**temp_config)
    cursor = conn.cursor()

    # 公告表
    cursor.execute('''CREATE TABLE IF NOT EXISTS announcements(
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        content TEXT NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # 反馈表
    cursor.execute('''CREATE TABLE IF NOT EXISTS feedback(
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_name VARCHAR(255) NOT NULL,
        message TEXT NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # 用户表
    cursor.execute('''CREATE TABLE IF NOT EXISTS users(
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        is_admin INT DEFAULT 0)''')

    # 创建默认分管理员账号
    cursor.execute("SELECT * FROM users WHERE is_admin = 1")
    if cursor.fetchone() is None:
        admin_pass = hashlib.sha256('admin'.encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s)", ('admin', admin_pass, 1))

    conn.commit()
    cursor.close()
    conn.close()
    print("数据库表已成功初始化 (PyMySQL, is_admin as INT)。")


# 密码哈希处理
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# 用户认证路由
@app.route('/api/login', methods=['POST'])
def login_user():
    username = request.form['username']
    password = request.form['password']
    if not username or not password:
        flash("用户名和密码不能为空！")
        return redirect(url_for('show_login'))
    conn = get_db_connection()
    if conn is None:
        flash("数据库服务暂时不可用，请稍后再试。")
        return redirect(url_for('show_login'))
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
    conn.close()
    if user is None or hash_password(password) != user['password']:
        flash("用户名或密码错误！")
        return redirect(url_for('show_login'))
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['is_admin'] = user['is_admin']
    return redirect(url_for('index'))


@app.route('/logout')
def logout_user():
    session.clear()
    flash("您已成功退出登录。")
    return redirect(url_for('show_login'))


# 首页
@app.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('show_login'))
    conn = get_db_connection()
    if conn is None: return "数据库连接失败，无法加载公告。", 500
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM announcements ORDER BY date DESC")
        announcements = cursor.fetchall()
    conn.close()
    return render_template('index.html', announcements=announcements, session=session)


# 反馈页
@app.route('/feedback', methods=['GET', 'POST'])
def feedback_page():
    if 'user_id' not in session: return redirect(url_for('show_login'))
    if request.method == 'POST':
        user_name = session.get('username', 'Anonymous')
        message = request.form['message']
        conn = get_db_connection()
        if conn is None:
            flash("数据库连接错误，反馈提交失败。")
            return redirect(url_for('feedback_page'))
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO feedback (user_name, message) VALUES (%s, %s)", (user_name, message))
        conn.commit()
        conn.close()
        flash("反馈提交成功，感谢您的意见！")
        return redirect(url_for('feedback_page'))
    return render_template('feedback.html', session=session)


# 后台
# --- 后台管理CRUD路由 ---
@app.route('/admin')
def admin_dashboard():
    # 【修改】使用明确的 == 1 判断
    if session.get('is_admin') != 1:
        flash("您没有权限访问此页面！")
        return redirect(url_for('index'))
    conn = get_db_connection()
    if conn is None: return "数据库连接失败，无法加载管理后台。", 500
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM announcements ORDER BY date DESC")
        announcements = cursor.fetchall()
        cursor.execute("SELECT * FROM feedback ORDER BY date DESC")
        feedbacks = cursor.fetchall()
        cursor.execute("SELECT * FROM users ORDER BY id")
        users = cursor.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', announcements=announcements, feedbacks=feedbacks, users=users,
                           session=session)


# 公告（增）
@app.route('/admin/announcement/add', methods=['POST'])
def add_announcement():
    if session.get('is_admin') != 1: return redirect(url_for('index'))
    title = request.form['title']
    content = request.form['content']
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO announcements (title, content) VALUES (%s, %s)", (title, content))
    conn.commit()
    conn.close()
    flash("公告发布成功！")
    return redirect(url_for('admin_dashboard'))


# 公告（更新）
@app.route('/admin/announcement/edit/<int:id>', methods=['GET', 'POST'])
def edit_announcement(id):
    if session.get('is_admin') != 1: return redirect(url_for('index'))
    conn = get_db_connection()
    with conn.cursor() as cursor:
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            cursor.execute("UPDATE announcements SET title = %s, content = %s WHERE id = %s", (title, content, id))
            conn.commit()
            flash("公告更新成功！")
            return redirect(url_for('admin_dashboard'))

        cursor.execute("SELECT * FROM announcements WHERE id = %s", (id,))
        announcement = cursor.fetchone()
    conn.close()
    return render_template('edit_announcement.html', announcement=announcement, session=session)


# 公告（删除）
@app.route('/admin/announcement/delete/<int:id>', methods=['POST'])
def delete_announcement(id):
    if session.get('is_admin') != 1: return redirect(url_for('index'))
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM announcements WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    flash("公告删除成功！")
    return redirect(url_for('admin_dashboard'))


# 用户（创建）
@app.route('/admin/user/add', methods=['POST'])
def add_user():
    if session.get('is_admin') != 1: return redirect(url_for('index'))
    username = request.form['username']
    password = request.form['password']
    # 【修改】将布尔值转换为 0 或 1
    is_admin = 1 if 'is_admin' in request.form else 0
    if not username or not password:
        flash("用户名和密码不能为空！")
        return redirect(url_for('admin_dashboard'))

    hashed_password = hash_password(password)
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (%s, %s, %s)",
                           (username, hashed_password, is_admin))
        conn.commit()
        flash("用户创建成功！")
    except pymysql.IntegrityError:
        flash("用户名已存在！")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('admin_dashboard'))


# 用户（更新）
@app.route('/admin/user/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    if session.get('is_admin') != 1: return redirect(url_for('index'))
    conn = get_db_connection()
    with conn.cursor() as cursor:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            is_admin = 1 if 'is_admin' in request.form else 0

            if password:
                hashed_password = hash_password(password)
                cursor.execute("UPDATE users SET username = %s, password = %s, is_admin = %s WHERE id = %s",
                               (username, hashed_password, is_admin, id))
            else:
                cursor.execute("UPDATE users SET username = %s, is_admin = %s WHERE id = %s", (username, is_admin, id))
            conn.commit()
            flash("用户信息更新成功！")
            return redirect(url_for('admin_dashboard'))
        cursor.execute("SELECT * FROM users WHERE id = %s", (id,))
        user = cursor.fetchone()
    conn.close()
    return render_template('edit_user.html', user=user, session=session)


# 用户（删除）
@app.route('/admin/user/delete/<int:id>', methods=['POST'])
def delete_user(id):
    if session.get('is_admin') != 1: return redirect(url_for('index'))
    if id == session['user_id']:
        flash("危险操作：不能删除当前登录的账户！")
        return redirect(url_for('admin_dashboard'))
    if id == 1:
        flash("禁止删除超级管理员账户！")
        return redirect(url_for('admin_dashboard'))
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM users WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    flash("用户删除成功！")
    return redirect(url_for('admin_dashboard'))


# 反馈（删除）
@app.route('/admin/feedback/delete/<int:id>', methods=['POST'])
def delete_feedback(id):
    if session.get('is_admin') != 1: return redirect(url_for('index'))
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM feedback WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    flash("反馈删除成功！")
    return redirect(url_for('admin_dashboard'))


# 登录页面路由
@app.route('/login', methods=['GET'])
def show_login():
    return render_template('login_register.html')


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
