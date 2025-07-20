from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from argon2 import PasswordHasher

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ph = PasswordHasher()

# Tabela do banco de dados
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)

# Criar o banco na primeira execução
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form['usuario']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(nome=nome).first()
        if usuario:
            try:
                ph.verify(usuario.senha_hash, senha)
                return f'Bem-vindo, {nome}!'
            except:
                return 'Senha incorreta.'
        else:
            return 'Usuário não encontrado.'
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['usuario']
        senha = request.form['senha']
        if Usuario.query.filter_by(nome=nome).first():
            return 'Usuário já existe.'
        senha_hash = ph.hash(senha)
        novo_usuario = Usuario(nome=nome, senha_hash=senha_hash) # type: ignore
        db.session.add(novo_usuario)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('cadastro.html')

if __name__ == '__main__':
    app.run(debug=True)