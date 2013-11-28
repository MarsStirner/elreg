# -*- coding: utf-8 -*-
import os
from ast import literal_eval
from flask import render_template, abort, request, redirect, url_for, flash, session, current_app
from flask.views import MethodView

from jinja2 import TemplateNotFound
from flask_wtf import Form
from wtforms import StringField, PasswordField, IntegerField, SelectField, BooleanField, FileField, TextAreaField
from wtforms.validators import Required
from flask.ext.principal import Identity, AnonymousIdentity, identity_changed
from flask.ext.principal import identity_loaded, Permission, RoleNeed, UserNeed
from flask.ext.login import login_user, logout_user, login_required, current_user

from application.app import app, db, login_manager
from models import Settings, Users, Roles
from lib.user import User
from forms import EditUserForm, LoginForm
from lib.utils import admin_permission, public_endpoint, logger

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise ImportError

from lib.captcha.views import get_captcha_image
get_captcha_image = public_endpoint(get_captcha_image)

login_manager.login_view = 'login'


def exclude_endpoint(endpoint, exclude):
    for item in exclude:
        if item in endpoint:
            return True
    return False


@app.before_request
def check_valid_login():
    login_valid = current_user.is_authenticated()

    exclude_list = ['static']
    exclude_list.extend(getattr(current_app, 'blueprints', list()).keys())

    if (request.endpoint and
            not exclude_endpoint(request.endpoint, exclude_list) and
            not login_valid and
            not getattr(app.view_functions[request.endpoint], 'is_public', False)):
        return redirect(url_for('login', next=url_for(request.endpoint)))


@app.route('/admin/')
def index():
    return render_template('index.html')


def _get_field_class(value_type):
    if value_type == 'string':
        _cls = StringField
    elif value_type == 'bool':
        _cls = BooleanField
    elif value_type == 'enum':
        _cls = SelectField
    elif value_type == 'number':
        _cls = IntegerField
    elif value_type == 'image':
        _cls = FileField
    elif value_type == 'password':
        _cls = StringField
    elif value_type == 'text':
        _cls = TextAreaField
    else:
        _cls = StringField
    return _cls


def _create_field(variable):
    _cls = _get_field_class(variable.value_type)
    if variable.value_type == 'enum':
        obj = _cls(variable.code, default="", description=variable.name, choices=json.loads(variable.defaults))
    else:
        obj = _cls(variable.code, default="", description=variable.name)
    return obj


@app.route('/admin/settings/', methods=['GET', 'POST'])
@admin_permission.require(http_exception=403)
def settings():
    try:
        class ConfigVariablesForm(Form):
            pass

        variables = db.session.query(Settings).order_by('id').all()
        values = dict()
        for variable in variables:
            setattr(ConfigVariablesForm,
                    variable.code,
                    _create_field(variable))
            values[variable.code] = variable.value
            if variable.value_type == 'bool':
                if values[variable.code]:
                    values[variable.code] = bool(literal_eval(values[variable.code]))
                else:
                    values[variable.code] = False

        form = ConfigVariablesForm(request.form, **values)
        #for variable in variables:
        #    form[variable.code].value = variable.value if variable.value is not None else ""

        if form.validate_on_submit():
            for variable in variables:
                variable.value = form.data[variable.code]
                if variable.value_type == 'image' and request.files[form[variable.code].name]:
                    image_data = request.files[form[variable.code].name].read()
                    open(os.path.join(app.static_folder, 'i', request.files[form[variable.code].name].filename), 'w').write(image_data)
                    variable.value = request.files[form[variable.code].name].filename

            db.session.commit()
            flash(u'Настройки изменены')
            return redirect(url_for('settings'))

        return render_template('settings.html', form=form)
    except TemplateNotFound:
        abort(404)


@app.route('/admin/login/', methods=['GET', 'POST'])
@public_endpoint
def login():
    # login form that uses Flask-WTF
    form = LoginForm()
    errors = list()

    # Validate form input
    if form.validate_on_submit():
        # Retrieve the user from the hypothetical datastore
        user = db.session.query(Users).filter(Users.login == form.login.data.strip()).first()
        if user:
            check_user = User(user.login)
            # Compare passwords (use password hashing production)
            if check_user.check_password(form.password.data.strip(), user.password):
                # Keep the user info in the session using Flask-Login
                login_user(user)

                # Tell Flask-Principal the identity changed
                identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))

                return redirect(request.args.get('next') or url_for('index'))
            else:
                errors.append(u'Неверная пара логин/пароль')
        else:
            errors.append(u'Нет пользователя с логином <b>%s</b>' % form.login.data.strip())

    return render_template('user/login.html', form=form, errors=errors)


@app.route('/admin/logout/')
def logout():
    # Remove the user information from the session
    logout_user()

    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app._get_current_object(), identity=AnonymousIdentity())

    return redirect(request.args.get('next') or '/admin/')


@app.route('/admin/users/')
@admin_permission.require(http_exception=403)
def users():
    # return a list of users
    return render_template('user/list.html', users=db.session.query(Users).order_by(Users.id).all())


@app.route('/admin/users/add/', methods=['GET', 'POST'])
@admin_permission.require(http_exception=403)
def post_user():
    # create a new user
    db_roles = db.session.query(Roles).all()
    radio_roles = [(role.id, role.name) for role in db_roles]
    form = EditUserForm()
    form.role.choices = radio_roles
    if form.validate_on_submit():
        user = User(form.login.data.strip(), form.password.data.strip())
        if db.session.query(Users).filter(Users.login == user.login).count() > 0:
            return render_template('user/edit.html',
                                   errors=[u'Пользователь с логином <b>%s</b> уже существует' % user.login], form=form)
        db_user = Users(user.login, user.pw_hash)
        db_role = db.session.query(Roles).get(form.role.data)
        db_user.roles.append(db_role)
        db.session.add(db_user)
        db.session.commit()
        flash(u'Пользователь добавлен')
        return redirect(url_for('users'))
    return render_template('user/edit.html', form=form)


@app.route('/admin/users/<int:user_id>/', methods=['GET', 'POST'])
@admin_permission.require(http_exception=403)
def put_user(user_id):
    db_user = db.session.query(Users).get(user_id)
    if db_user is None:
        return render_template('user/list.html',
                               users=db.session.query(Users).order_by(Users.id).all(),
                               errors=u'Пользователя с id=%s не существует' % user_id)
    db_roles = db.session.query(Roles).all()
    radio_roles = [(role.id, role.name) for role in db_roles]
    form = EditUserForm(login=db_user.login)
    form.role.choices = radio_roles
    if form.validate_on_submit():
        password = form.password.data.strip()
        if password:
            user = User(form.login.data.strip(), form.password.data.strip())
            db_user.password = user.pw_hash
        else:
            user = User(form.login.data.strip())

        if db_user.login != user.login and db.session.query(Users).filter(Users.login == user.login).count() > 0:
            return render_template('user/edit.html',
                                   errors=[u'Пользователь с логином <b>%s</b> уже существует' % user.login], form=form)
        db_user.login = user.login
        db_role = db.session.query(Roles).get(form.role.data)
        db_user.roles[0] = db_role
        db.session.commit()
        flash(u'Пользователь изменен')
        return redirect(url_for('users'))
    return render_template('user/edit.html', form=form, user=db_user)


@app.route('/admin/users/delete/<int:user_id>/', methods=['POST'])
@admin_permission.require(http_exception=403)
def delete_user(user_id):
    # delete a single user
    errors = list()
    try:
        user = db.session.query(Users).get(user_id)
        db.session.delete(user)
        db.session.commit()
    except Exception, e:
        errors.append(u'Ошибка при удалении пользователя: %s' % e)
    else:
        flash(u'Пользователь удалён')
        return redirect(url_for('users'))
    return render_template('user/list.html', users=db.session.query(Users).order_by(Users.id).all(), errors=errors)


@app.errorhandler(403)
def authorisation_failed(e):
    logger.error(e, extra=dict(tags=[u'authorisation_failed (403)', 'elreg']))
    flash(u'У вас недостаточно привилегий для доступа к функционалу')
    return render_template('user/denied.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.errorhandler(500)
def internal_error(e):
    logger.error(e, extra=dict(tags=[u'internal_error (500)', 'elreg']))
    return render_template('500.html'), 500


#########################################

@login_manager.user_loader
def load_user(user_id):
    # Return an instance of the User model
    return db.session.query(Users).get(user_id)


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    if identity.id:
        identity.user = load_user(identity.id)

        # Add the UserNeed to the identity
        if hasattr(identity.user, 'id'):
            identity.provides.add(UserNeed(identity.user.id))

        # Assuming the User model has a list of roles, update the
        # identity with the roles that the user provides
        if hasattr(identity.user, 'roles'):
            for role in identity.user.roles:
                identity.provides.add(RoleNeed(role.code))