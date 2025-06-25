# Imports
import sqlite3

# Conectando ao DB
conn = sqlite3.connect('fishes.db')

# Criando um cursor
cursor = conn.cursor()

# Criando a tabela dos peixes
cursor.execute("""
CREATE TABLE IF NOT EXISTS population (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT
               )
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS individuals (
               id TEXT PRIMARY KEY,
               father_id TEXT,
               mother_id TEXT,
               generation INTEGER,
               gender TEXT,
               timestamp TEXT,
               population_id INTEGER,
               FOREIGN KEY(father_id) REFERENCES individuals(id),
               FOREIGN KEY(mother_id) REFERENCES individuals(id),
               FOREIGN KEY(population_id) REFERENCES population(id)
               )
""")               

cursor.execute("""
CREATE TABLE IF NOT EXISTS karyotype (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               individual_id TEXT,
               karyotype TEXT,
               chromosome_origin TEXT,
               cutting_points TEXT,
               method TEXT,
               FOREIGN KEY(individual_id) REFERENCES individuals(id)
               )
""")

conn.commit()
conn.close()