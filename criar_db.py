
# criar_db.py
import sqlite3

# Conectar ao banco (ele cria o arquivo se não existir)
conn = sqlite3.connect('lojas.db')
cursor = conn.cursor()

# Criar a tabela "lojas"
cursor.execute('''
CREATE TABLE IF NOT EXISTS lojas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    desconto INTEGER NOT NULL
)
''')

# Inserir algumas lojas de exemplo (opcional)
lojas = [
    ('Loja A', -23.561414, -46.655881, 10),
    ('Loja B', -23.564333, -46.653423, 20),
    ('Loja C', -23.559768, -46.662489, 15)
]

cursor.executemany('INSERT INTO lojas (nome, latitude, longitude, desconto) VALUES (?, ?, ?, ?)', lojas)

conn.commit()
conn.close()
