# -*- coding: utf-8 -*-
from flask import Flask,render_template,redirect,url_for,request,current_app
app = Flask(__name__)
from flask_wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
import os
from datetime import datetime
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.mail import Message
from flask.ext.moment import Moment

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
bootstrap = Bootstrap(app)
CSRF_ENABLED = True
app.config['SECRET_KEY'] = 'hard-to-guss'
manager = Manager(app)
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
db = SQLAlchemy(app)
app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = 25
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '18677522661@163.com'
app.config['MAIL_PASSWORD'] = 'pegasus405'
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = '18677522661@163.com'
app.config['FLASKY_ADMIN'] = 'zaojue405@aliyun.com'
app.config['FLASKY_POSTS_PER_PAGE'] = 20
mail = Mail(app)#必须放在配置之后，等配置初始化并运行
moment = Moment(app)

def send_email(to,subject,template,**kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] +  ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt',**kwargs)
    msg.html = render_template(template +'.html',**kwargs)
    mail.send(msg)

class Post(db.Model):
    __tablename__= 'posts'
    id = db.Column(db.Integer,primary_key = True)
    title = db.Column(db.String(64))
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True,default=datetime.utcnow)


    def __repr__(self):
        return '<Post.title %r>' % self.title

class PostForm(Form):
    title = StringField('title')
    body = TextAreaField("What's on your mind?", validators=[Required()])
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if form.validate_on_submit():
        
        post = Post(title=form.title.data,body=form.body.data)
        db.session.add(post)
        send_email(app.config['FLASKY_ADMIN'], 'NEW CONTEXT','mail/new_context',post=post)
        return redirect(url_for('.index'))
    page = request.args.get('page',1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', form = form,posts=posts,pagination=pagination)
        
@app.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', posts=[post])

if __name__=='__main__':
    manager.run()