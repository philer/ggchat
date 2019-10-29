#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'GGChat2018'
socketio = SocketIO(app)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/ggchat.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ggchat:Hixohm5p@localhost/ggchat'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_ECHO'] = True
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text(1000), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return 'Message({id}, "{author}", {created_at}, "{content}")'.format(
            id=self.id,
            author=self.author,
            created_at=self.created_at,
            content=self.content[:20] + "…" if len(self.content) > 21 else self.content)

    # def to_sql(self):
    #     for key in
    #     return ("INSERT INTO message (author, created_at, content)"
    #             "VALUES ('{}', '{:%Y-%m-%d %H:%M:%S}', '{}')").format(
    #                 self.author.replace("'", r"\'"),
    #                 self.created_at,
    #                 self.content.replace("'", r"\'"),
    #             )

@app.route('/')
def index():
    return render_template("base.html")

@socketio.on('startup')
def handle_startup(username):
    q = Message.query
    app.logger.info(str(q))
    return "".join(render_template("message.html",
                                   message=message,
                                   own=message.author == username)
                   for message in q.all())

@socketio.on('msg')
def handle_json(json):
    message = Message(**json)
    # app.logger.info(message)
    # app.logger.info(message.to_sql())
    db.session.add(message)
    db.session.commit()
    app.logger.info(message)
    app.logger.info(message.query_class)
    send(render_template("message.html", message=message),
         broadcast=True, include_self=False)
    return render_template("message.html", message=message, own=True)

@socketio.on('connect')
def test_connect():
    app.logger.info("connected %s", request.access_route)

@socketio.on('disconnect')
def test_disconnect():
    app.logger.info("disconnected %s", request.access_route)


if __name__ == '__main__':
    # db.create_all()  # doesn't do anything - why?
    # db.session.commit()
    import os
    if os.getuid() == 0:
        print("Starting server at 0.0.0.0:80")
        socketio.run(app, host="0.0.0.0", port=80)
    else:
        print("Starting server at localhost:9000")
        socketio.run(app, port=9000)
