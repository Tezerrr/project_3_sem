from flask import Flask, jsonify, request
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from sqlalchemy import create_engine
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

from main_recognition import model,img_to_str
from api.config import Config
from flask_cors import CORS


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config.from_object(Config)  # извлекаем данные из файла config.py

client = app.test_client()
# инициализируем связь с базой данных
engine = create_engine("postgresql+psycopg2://postgres:postgres@localhost/flaskapi")

session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()
jwt = JWTManager(app)
from api.models import *  # импортируем таблицу
Base.metadata.create_all(bind=engine)


@app.route('/register', methods=['POST'], endpoint='register')  # метод регистрации пользователя
def register():
    params = request.json
    user = User(**params)
    session.add(user)
    session.commit()
    access_token = user.get_access_token()
    refresh_token = user.get_refresh_token()
    return {'access_token': access_token, 'refresh token': refresh_token}


@app.route('/login', methods=['GET', 'POST'], endpoint='login')  # метод авторизации пользователя
def login():
    params = request.json
    try:
        item = User.query.filter(User.email == params['email']).first()
        crutch = {'id': item.id, 'username': item.username, 'email': item.email, 'password': item.password}
    except AttributeError:
        pass
    user = User.autenticate(**params)
    access_token = user.get_access_token()
    refresh_token = user.get_refresh_token()
    return {'access_token': access_token, 'refresh token': refresh_token, 'username': crutch['username']}


@app.route('/delete', methods=['DELETE'], endpoint='delete_user')  # удаление пользователя
@jwt_required()
def delete_user():
    user_id = get_jwt_identity()
    item = User.query.filter(User.id == user_id).first()
    if not item:
        return {'message': 'User alredy deleted'}, 400
    session.delete(item)
    session.commit()
    return '', 204


@app.route('/refresh', methods=['POST'], endpoint='refresh')  # метод обновления jwt-токена
@jwt_required(refresh=True)
def refresh():
    profile_id = get_jwt_identity()
    access_token = create_access_token(identity=profile_id)
    refresh_token= create_refresh_token(identity=profile_id)
    return jsonify(access_token=access_token, refresh_token=refresh_token)

@app.route('/recognition', methods=['GET','POST'], endpoint='recognition')# метод для обработки изображения
def recognition():
    img=request.get_data()
    f = request.files['jpg']
    f.save('image.jpg')
    response= img_to_str(model, f)
    return response


@app.teardown_appcontext
def shutdown_session(exception=None):
    session.remove()