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
    

    peso_real_trab = db.Column(db.Float, nullable=False)
    peso_real_av = db.Column(db.Float, nullable=False)
    peso_orig_av = db.Column(db.Float, nullable=False)

class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    nota_final_calculada = db.Column(db.Float, nullable=False)
    nota_trab = db.Column(db.Float, nullable=True)
    nota_av = db.Column(db.Float, nullable=True)
    nota_avs = db.Column(db.Float, nullable=True)
    nota_trab_oficial = db.Column(db.Float, nullable=False)
    nota_av_ponderada = db.Column(db.Float, nullable=False)
    sobra_trab = db.Column(db.Float, nullable=False)
    classificacao_id = db.Column(db.Integer, db.ForeignKey('classificacao.id'), nullable=False)

    def to_dict(self):
        return {
            'nome': self.nome,
            'nota_trab': self.nota_trab,
            'nota_av': self.nota_av,
            'nota_avs': self.nota_avs,
            'nota_trab_oficial': self.nota_trab_oficial,
            'nota_av_ponderada': self.nota_av_ponderada,
            'sobra_trab': self.sobra_trab,
            'nota_final_calculada': self.nota_final_calculada
        }


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Página principal do sistema de classificação.
    
    Se o método for for 'POST', tenta processar o upload de um arquivo de planilha e criar uma nova classificação com os pesos fornecidos.
    Se houver algum erro no processamento, retorna a página com o erro.
    Se não houver erros, retorna a página com a lista de todas as classificações criadas.
    """
    erro = None
    if request.method == 'POST':
        try:
            if 'file' not in request.files:
                raise ValueError("Nenhum arquivo selecionado.")
            file = request.files['file']
            
            nome_disciplina = request.form['nome_disciplina']
            peso_real_trab = float(request.form['peso_real_trab'])
            peso_real_av = float(request.form['peso_real_av'])
            peso_orig_av = float(request.form['peso_orig_av'])
            
            if file.filename == '' or nome_disciplina == '':
                 raise ValueError("Preencha todos os campos do formulário.")
            
            if peso_orig_av == 0:
                 raise ValueError("A 'Base de Nota AV/AVS' não pode ser zero.")

            classificacao = Classificacao.query.filter_by(nome_disciplina=nome_disciplina).first()
            if classificacao:
                classificacao.peso_real_trab = peso_real_trab
                classificacao.peso_real_av = peso_real_av
                classificacao.peso_orig_av = peso_orig_av
            else:
                classificacao = Classificacao(
                    nome_disciplina=nome_disciplina,
                    peso_real_trab=peso_real_trab,
                    peso_real_av=peso_real_av,
                    peso_orig_av=peso_orig_av
                )
                db.session.add(classificacao)
                
            db.session.commit()
            
            try:
                df = pd.read_csv(file)
            except Exception:
                df = pd.read_excel(file)
            
            for index, row in df.iterrows():
                nome = row.get('nome', 'Aluno Sem Nome')
                nota_trab_planilha = float(row.get('Trab', 0) or 0)
                nota_av_planilha = float(row.get('AV', 0) or 0)
                nota_avs_planilha = float(row.get('AVS', 0) or 0)

                nota_final_trab = min(nota_trab_planilha, peso_real_trab)
                sobra_trab = max(0, nota_trab_planilha - peso_real_trab)
                nota_av_efetiva = max(nota_av_planilha, nota_avs_planilha)
                nota_av_ponderada = (nota_av_efetiva / peso_orig_av) * peso_real_av
                nota_final_calculada = min(nota_final_trab + nota_av_ponderada + sobra_trab, 10)
                
                novo_aluno = Aluno(
                    nome=nome,
                    nota_trab=nota_trab_planilha,
                    nota_av=nota_av_planilha,
                    nota_avs=nota_avs_planilha,
                    
                    nota_trab_oficial=round(nota_final_trab, 2),
                    nota_av_ponderada=round(nota_av_ponderada, 2),
                    sobra_trab=round(sobra_trab, 2),
                    
                    nota_final_calculada=round(nota_final_calculada, 2),
                    classificacao_id=classificacao.id
                )
                db.session.add(novo_aluno)
            
            db.session.commit()
            return redirect(url_for('index'))

        except (ValueError, KeyError, TypeError) as e:
            erro = f"Erro no processamento: {e}. Verifique as colunas ('nome', 'Trab', 'AV', 'AVS') e os pesos."
            db.session.rollback()
        except Exception as e:
            erro = f"Erro inesperado no upload: {e}"
            db.session.rollback()

    classificacoes = Classificacao.query.all()
    return render_template('index.html', classificacoes=classificacoes, erro=erro)


@app.route('/ranking/<int:id_classificacao>')
def ver_ranking(id_classificacao):
    try:
        classificacao = Classificacao.query.get_or_404(id_classificacao)
        
        alunos_do_banco = classificacao.alunos
        lista_para_ordenar = []
        for aluno in alunos_do_banco:
            aluno_dict = aluno.to_dict()
            aluno_dict['nota_av_efetiva'] = max(
                aluno_dict['nota_av'] or 0, 
                aluno_dict['nota_avs'] or 0
            )
            lista_para_ordenar.append(aluno_dict)
        
        ranking_ordenado = merge_sort(lista_para_ordenar, key='nota_final_calculada', descending=True)

        ranking_com_posicao = []
        last_score = -1
        current_rank = 0
        
        for i, aluno in enumerate(ranking_ordenado):
            if aluno['nota_final_calculada'] != last_score:
                current_rank = i + 1
                last_score = aluno['nota_final_calculada']
            
            aluno['posicao'] = current_rank 
            ranking_com_posicao.append(aluno)
        
        return render_template('ranking.html', 
                               ranking=ranking_com_posicao, 
                               classificacao=classificacao)
    
    except Exception as e:
        return f"Erro ao gerar ranking: {e}", 400
    
@app.route('/delete/<int:id_classificacao>', methods=['POST'])
def delete_classificacao(id_classificacao):
    """
    Exclui a classificação com o ID fornecido.

    Parameters:
    id_classificacao (int): ID da classificação a ser excluida.

    Returns:
    redirect: Redireciona para a página inicial.
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