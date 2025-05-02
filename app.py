from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import math
from datetime import datetime, timedelta

app = Flask(__name__)

# Função para criar a tabela no banco de dados
def criar_tabela():
    conn = sqlite3.connect('lojas.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lojas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            desconto INTEGER NOT NULL,
            data_criacao TEXT NOT NULL,
            validade_dias INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Função para calcular a distância
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371  # Raio da Terra em km
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# Página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Página de administração
@app.route('/admin')
def admin():
    conn = sqlite3.connect('lojas.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome, descricao, latitude, longitude, desconto, data_criacao, validade_dias FROM lojas')
    lojas = cursor.fetchall()
    conn.close()
    return render_template('admin.html', lojas=lojas)

# Página de cadastro
@app.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        desconto = request.form['desconto']
        validade_dias = request.form.get('validade_dias', 7)

        conn = sqlite3.connect('lojas.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO lojas (nome, descricao, latitude, longitude, desconto, data_criacao, validade_dias)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nome, descricao, latitude, longitude, desconto, datetime.now().isoformat(), validade_dias))
        conn.commit()
        conn.close()

        return redirect('/admin')
    return render_template('cadastrar.html')

# Rota para buscar lojas próximas
@app.route('/buscar_lojas', methods=['POST'])
def buscar_lojas():
    data = request.get_json()
    user_lat = data['latitude']
    user_lon = data['longitude']

    conn = sqlite3.connect('lojas.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome, descricao, latitude, longitude, desconto, data_criacao, validade_dias FROM lojas')
    lojas = cursor.fetchall()
    conn.close()

    lojas_proximas = []
    agora = datetime.now()

    for loja in lojas:
        id_loja, nome, descricao, lat, lon, desconto, data_criacao, validade_dias = loja
        data_criacao_dt = datetime.fromisoformat(data_criacao)
        validade = data_criacao_dt + timedelta(days=int(validade_dias))

        if agora <= validade:
            distancia = calcular_distancia(user_lat, user_lon, lat, lon)
            lojas_proximas.append({
                'id': id_loja,
                'nome': nome,
                'descricao': descricao,
                'latitude': lat,
                'longitude': lon,
                'desconto': desconto,
                'distancia': round(distancia, 2)
            })

    lojas_proximas.sort(key=lambda x: x['distancia'])
    return jsonify(lojas_proximas)

# Excluir loja
@app.route('/excluir_loja/<int:loja_id>', methods=['POST'])
def excluir_loja(loja_id):
    conn = sqlite3.connect('lojas.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM lojas WHERE id = ?', (loja_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')

# Editar loja

@app.route('/editar_loja/<int:loja_id>', methods=['GET'])
def editar_loja(loja_id):
    conn = sqlite3.connect('lojas.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome, descricao, latitude, longitude, desconto, validade_dias FROM lojas WHERE id = ?', (loja_id,))
    loja = cursor.fetchone()
    conn.close()
    if loja:
        return render_template('editar_loja.html', loja=loja)
    else:
        return "Loja não encontrada", 404

@app.route('/atualizar_loja/<int:loja_id>', methods=['POST'])
def atualizar_loja(loja_id):
    nome = request.form['nome']
    descricao = request.form['descricao']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    desconto = request.form['desconto']
    validade_dias = request.form['validade_dias']

    conn = sqlite3.connect('lojas.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE lojas
        SET nome = ?, descricao = ?, latitude = ?, longitude = ?, desconto = ?, validade_dias = ?
        WHERE id = ?
    ''', (nome, descricao, latitude, longitude, desconto, validade_dias, loja_id))
    conn.commit()
    conn.close()

    return redirect('/admin')






# Rodar a aplicação
if __name__ == '__main__':
    criar_tabela()
    app.run(debug=True)
