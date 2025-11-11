import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from algoritmos import merge_sort

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///local_test.db')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Remove avisos
db = SQLAlchemy(app)

class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    nota = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {'nome': self.nome, 'nota': self.nota}

# --- Rotas da Aplicação ---

@app.route('/', methods=['GET', 'POST'])
def index():
    erro = None
    if request.method == 'POST':
        try:
            #ler o arquivo
            if 'file' not in request.files:
                raise ValueError("Nenhum arquivo selecionado.")
            file = request.files['file']
            if file.filename == '':
                 raise ValueError("Nome de arquivo vazio.")

            if file:
                try:
                    #verifica se o arquivo é csv
                    df = pd.read_csv(file)
                except Exception as e_csv:
                    try:
                        #verifica se o arquivo é excel
                        df = pd.read_excel(file)
                    except Exception as e_excel:
                         raise ValueError(f"Não foi possível ler o arquivo. Use CSV ou Excel.")
                
                # processa e salva no banco
                lista_alunos_df = df.to_dict('records')
                
                for item in lista_alunos_df:
                    if 'nome' not in item or 'nota' not in item:
                        raise KeyError("Colunas 'nome' ou 'nota' não encontradas.")
                    
                    novo_aluno = Aluno(nome=item['nome'], nota=float(item['nota']))
                    db.session.add(novo_aluno)
                
                #salva todos os alunos no banco
                db.session.commit()
                
                return redirect(url_for('index'))

        except (ValueError, KeyError) as e:
            erro = str(e)
            db.session.rollback()
        except Exception as e:
            erro = f"Erro inesperado no upload: {e}"
            db.session.rollback()

    ranking_ordenado = []
    try:
        alunos_bd = Aluno.query.all()

        lista_para_ordenar = [aluno.to_dict() for aluno in alunos_bd]
        
        if lista_para_ordenar:
            #aplica o algoritmo (mergesort)
            ranking_ordenado = merge_sort(lista_para_ordenar, key='nota', descending=True)

    except Exception as e:
        erro = f"Erro ao buscar dados do banco: {e}"

    return render_template('index.html', ranking=ranking_ordenado, erro=erro)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)