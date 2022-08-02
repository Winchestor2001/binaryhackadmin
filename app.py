from flask import Flask, render_template, url_for, redirect, request, flash, jsonify
from flask_login import login_user, login_required, LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy

from admin_login import AdminLogin

app = Flask(__name__)
app.secret_key = 'some secret key 8888'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///aviahack.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = '/login'


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(200), nullable=False, unique=True)
    user_password = db.Column(db.String(200), nullable=False)
    user_status = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Users {self.id}>'


class Admins(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(200), nullable=False, unique=True)
    user_password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Admins {self.id}>'


@login_manager.user_loader
def load_user(user_id):
    return Admins.query.get(user_id)


@app.route('/login', methods=['POST', 'GET'])
def login_admin():
    if request.method == 'POST':
        form = request.form
        if form['login'] and form['password']:
            admin = Admins.query.filter_by(user_name=form['login']).first()
            if admin and admin.user_password.lower() == form['password'].lower():
                login_user(admin)
                users = Users.query.all()
                return render_template('users.html', users=users)
            else:
                flash('Логин или пароль неверны')
        else:
            flash('Логин или пароль не заполнены')
    return render_template('home.html')


@app.route('/', methods=['POST', 'GET'])
@login_required
def home():
    return render_template('home.html')


@app.route('/users', methods=['POST', 'GET'])
@login_required
def show_users():
    users = Users.query.all()
    return render_template('users.html', users=users)


@app.route('/edit/<int:id>/<status>')
def edit_user_data(id, status):
    user = Users.query.get(id)
    if status == 'del':
        db.session.delete(user)
        db.session.commit()
        users = Users.query.all()
        return render_template('users.html', users=users)
    elif status == 'error':
        user.user_status = 'Ошибка'
    elif status == 'up':
        user.user_status = 'Вверх'
    elif status == 'down':
        user.user_status = 'Вниз'
    try:
        db.session.commit()
    except Exception as ex:
        return f"Error - {ex}"

    users = Users.query.all()
    return render_template('users.html', users=users)


@app.route('/add_user', methods=['POST', 'GET'])
@login_required
def add_user():
    if request.method == 'POST':
        form = request.form
        if form['login'] and form['password']:
            add_user_data = Users(user_name=form['login'], user_password=form['password'], user_status='no')
            try:
                db.session.add(add_user_data)
                db.session.commit()
                return redirect('/users')
            except:
                error = f"Юзер с логином {form['login']} уже есть в базе"
                return render_template('add_user.html', error=error)
        error = 'Заполните полностью'
        return render_template('add_user.html', error=error)
    return render_template('add_user.html')


@app.route('/check_user/<login>/<password>', methods=['POST'])
def check_user(login, password):
    if request.method == 'POST':
        user = Users.query.filter_by(user_name=login).first()
        if user and user.user_password and user.user_password.lower() == password.lower():
            return jsonify({'status': True})
        else:
            return jsonify({'status': False})


@app.route('/get/<login>', methods=['POST'])
def get_user_status(login):
    if request.method == 'POST':
        user = Users.query.filter_by(user_name=login).first()
        if user:
            data = {'status': user.user_status}
            user.user_status = 'no'
            try:
                db.session.commit()
            except:
                pass
            return jsonify(data)

        else:
            return jsonify({'status': False})


if __name__ == '__main__':
    app.run(debug=True)
