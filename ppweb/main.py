import sqlite3
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, logout_user, login_required, current_user, login_user

connection = sqlite3.connect('ba2 (4).db', check_same_thread=False)
cursor = connection.cursor()

app = Flask(__name__)
app.secret_key = 'Artem112012'  # Необходимо для flash-сообщений

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash =  password_hash

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="pbkd2:sha256")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    user = cursor.execute("SELECT * FROM user WHERE id = ?", (user_id,)).fetchone()
    if user is not None:
        return User(user[2], user[1], user[2])
    return None

# Функция для получения соединения с БД
def get_db_connection():
    conn = sqlite3.connect("ba2 (4).db")
    conn.row_factory = sqlite3.Row  # Для доступа к полям по имени
    return conn


@app.teardown_appcontext
def close_connection(exception):
    conn = getattr(Flask, '_database', None)
    if conn is not None:
        conn.close()

@login_required
@app.route("/add/", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        conn = get_db_connection()
        try:
            conn.execute(
                '''INSERT INTO post (title, content, author_id) VALUES (?, ?, ?)''',
                (title, content, current_user.id)
            )
            conn.commit()
            flash('Post added successfully!', 'success')
            return redirect(url_for("index"))
        except sqlite3.Error as e:
            flash(f'Error adding post: {str(e)}', 'error')
        finally:
            conn.close()
    return render_template("add_post.html")


@app.route("/blog/")
def blog():

    conn = get_db_connection()
    try:
        posts = conn.execute('''SELECT * from post JOIN user ON post.author_id = user.id''').fetchall()
        posts = [dict(post) for post in reversed(posts)]  # Конвертируем в словари
        return render_template("blog.html", posts=posts)
    finally:
        conn.close()


@app.route('/post/<int:post_id>')
def post(post_id):
    conn = get_db_connection()
    try:
        post = conn.execute(
            'SELECT * FROM post WHERE id = ?',
            (post_id,)
        ).fetchone()
        if post is None:
            flash('Post not found', 'error')
            return redirect(url_for('index'))
        return render_template('post.html', post=dict(post))
    finally:
        conn.close()


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')

        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('register.html')

        conn = get_db_connection()
        try:
            conn.execute(
                'INSERT INTO user (username, password_hash, email) VALUES (?, ?, ?)',
                (username, generate_password_hash(password, method="pbkdf2:sha256"), email)
            )
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))  # Предполагается, что у вас есть маршрут 'login'
        except sqlite3.IntegrityError:
            flash('Username already exists', 'error')
            return render_template('register.html')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = cursor.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()


        if user and User(user[0], user[1], user[2]).check_password(password):
            login_user(User(user[0], user[1], user[2]))
            return redirect(url_for("index"))
        else:
            return  render_template("login.html", message="Invalid usernmae or password")
    return render_template("login.html")

@app.route("/delete/<int:post_id>", methods=["POST"])
@login_required
def delete_post(post_id):
    conn = get_db_connection()
    try:
        post = conn.execute("SELECT * FROM post WHERE id = ?", (post_id,)).fetchone()
        if post and post['author_id'] == current_user.id:
            conn.execute('DELETE FROM post WHERE id = ?', (post_id,))
            conn.commit()
            flash('Post deleted!', 'success')
        else:
            flash('Permission denied or post not found', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    finally:
        conn.close()
    return redirect(url_for("index"))

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

def user_is_liking(user_id, post_id):
    like = cursor.execute('SELECT * FROM like WHERE user_id = ? AND post_id = ?', (user_id, post_id)).fetchone()
    return like is not None

@app.route('/like/<int:post_id>')
@login_required
def like_post(post_id):
    post = cursor.execute('SELECT * FROM post WHERE id = ?', (post_id,)).fetchone()
    if post:
        if user_is_liking(current_user.id, post_id):
            cursor.execute('DELETE FROM like WHERE user_id = ? AND post_id = ?', (current_user.id, post_id))
            connection.commit()
            print('You unliked this post')
        else:
            cursor.execute('INSERT INTO like (user_id, post_id) VALUES (?, ?)',(current_user.id, post_id))
            connection.commit()
            print('rrr')
        return redirect (url_for('index'))
    return 'Post not found', 404

@app.route('/')
def index():
    cursor.execute('''
            SELECT
                post.id,
                post.title,
                post.content,
                post.author_id,
                user.username,
                COUNT(like.id) AS likes
            FROM
                post
            JOIN
                user ON post.author_id = user.id
            LEFT JOIN
                like ON post.id = like.post_id
            GROUP BY
                post.id, post.title, post.content, post.author_id, user.username''')
    result = cursor.fetchall()
    posts = []
    for post in reversed(result):
        posts.append({'id': post[0], 'title': post[1], 'content': post[2], 'author_id': post[3], 'username': post[4], 'likes': post[5]})

    if current_user.is_authenticated:
        cursor.execute(
            'SELECT post_id FROM like WHERE user_id = ?', (current_user.id, )
        )
        likes_result = cursor.fetchall()
        liked_posts = [like[0] for like in likes_result]
        # Добавляем информацию о лайках к каждому посту
        for post in posts:
            post['liked'] = post['id'] in liked_posts

    context = {"posts": posts}
    return render_template('blog.html', **context)

# Добавление комментария
@app.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    content = request.form.get('content')
    if not content:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('view_post', post_id=post_id))

    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO comment (post_id, user_id, content, date) VALUES (?, ?, ?, ?)',
            (post_id, current_user.id, content, datetime.now())
        )
        conn.commit()
        flash('Comment added successfully', 'success')
    except sqlite3.Error as e:
        flash(f'Error adding comment: {str(e)}', 'error')
    finally:
        conn.close()

    return redirect(url_for('view_post', post_id=post_id))

# Удаление комментария
@app.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    conn = get_db_connection()
    try:
        comment = conn.execute(
            'SELECT * FROM comment WHERE id = ?',
            (comment_id,)
        ).fetchone()

        if not comment:
            flash('Comment not found', 'error')
        elif comment['user_id'] != current_user.id:
            flash('You can only delete your own comments', 'error')
        else:
            conn.execute(
                'DELETE FROM comment WHERE id = ?',
                (comment_id,)
            )
            conn.commit()
            flash('Comment deleted successfully', 'success')

        return redirect(url_for('view_post', post_id=comment['post_id']))
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(debug=True)
