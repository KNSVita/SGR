import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from algoritmos import merge_sort

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///local_test.db')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Classificacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_disciplina = db.Column(db.String(100), unique=True, nullable=False)
    alunos = db.relationship('Aluno', backref='classificacao', lazy=True, cascade="all, delete-orphan")

class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    nota = db.Column(db.Float, nullable=False)
    classificacao_id = db.Column(db.Integer, db.ForeignKey('classificacao.id'), nullable=False)

    def to_dict(self):
        return {'nome': self.nome, 'nota': self.nota}

# --- Rotas ---
@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Página inicial do sistema, onde é possível fazer o upload de uma planilha
    e criar uma classificação com base nessa planilha.

    Se o upload for realizado com sucesso, retorna uma redirect para a página
    inicial.

    Se ocorrer um erro durante o upload, retorna a página inicial com uma mensagem
    de erro.

    :return: Uma página HTML com a lista de classificações, ou uma página de erro
    com status 400.
    :rtype: str
    """
    erro = None
    if request.method == 'POST':
        try:
            #valida inputs
            if 'file' not in request.files:
                raise ValueError("Nenhum arquivo selecionado.")
            file = request.files['file']
            nome_disciplina = request.form['nome_disciplina']
            
            if file.filename == '' or nome_disciplina == '':
                 raise ValueError("Preencha o nome da disciplina e selecione um arquivo.")

            #verifica se a disciplina já existe se não cria
            classificacao = Classificacao.query.filter_by(nome_disciplina=nome_disciplina).first()
            if not classificacao:
                classificacao = Classificacao(nome_disciplina=nome_disciplina)
                db.session.add(classificacao)
                db.session.commit() 
            
            #le o arquivo
            try:
                #tenta ler como csv
                df = pd.read_csv(file)
            except Exception:
                #tenta ler como excel
                df = pd.read_excel(file)
            
            lista_alunos_df = df.to_dict('records')
            
            #cria os alunos
            for item in lista_alunos_df:
                if 'nome' not in item or 'nota' not in item:
                    raise KeyError("Colunas 'nome' ou 'nota' não encontradas.")
                
                novo_aluno = Aluno(
                    nome=item['nome'], 
                    nota=float(item['nota']),
                    classificacao_id=classificacao.id
                )
                db.session.add(novo_aluno)
            
            db.session.commit()
            return redirect(url_for('index'))

        except (ValueError, KeyError) as e:
            erro = str(e)
            db.session.rollback()
        except Exception as e:
            erro = f"Erro inesperado no upload: {e}"
            db.session.rollback()

    classificacoes = Classificacao.query.all()
    return render_template('index.html', classificacoes=classificacoes, erro=erro)


@app.route('/ranking/<int:id_classificacao>')
def ver_ranking(id_classificacao):

    """
    Mostra o ranking de uma disciplina, com base em seu ID.
    
    :param int id_classificacao: ID da classificação a ser exibida.
    :return: Uma página HTML com o ranking, ou uma página de erro com status 400.
    :rtype: str
    """
    try:
        #busca a classificação pelo id
        classificacao = Classificacao.query.get_or_404(id_classificacao)
        #busca os alunos
        alunos_bd = classificacao.alunos
        lista_para_ordenar = [aluno.to_dict() for aluno in alunos_bd]
        
        #ordena com mergesort
        ranking_ordenado = merge_sort(lista_para_ordenar, key='nota', descending=True)

        return render_template('ranking.html', 
                               ranking=ranking_ordenado, 
                               nome_disciplina=classificacao.nome_disciplina)
    
    except Exception as e:
        return f"Erro ao gerar ranking: {e}", 400
    
@app.route('/delete/<int:id_classificacao>', methods=['POST'])
def delete_classificacao(id_classificacao):
    """
    Exclui uma classificação pelo seu ID.
    
    :param int id_classificacao: ID da classificação a ser excluída.
    :return: Uma página HTML com o status 200, ou uma página de erro com status 400.
    :rtype: str
    """
    try:
        classificacao_para_excluir = Classificacao.query.get_or_404(id_classificacao)

        db.session.delete(classificacao_para_excluir)
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao excluir: {e}")

    return redirect(url_for('index'))


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)