# Imports
import sqlite3
import json

# Lista das operações do banco de dados

# Inserindo uma população na tabela
def add_population(name):
    
    conn = sqlite3.connect('fishes.db')
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO population (name)
        VALUES (?)
                   """, 
        (name,))
    conn.commit()
    last_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return last_id
    
# Inserindo um indivíduo na tabela
def add_individual(individual_dict, population_id=1):

    conn = sqlite3.connect('fishes.db')
    cursor = conn.cursor()

    indv_id = individual_dict['indv_id']
    father_id = individual_dict['father_id']
    mother_id = individual_dict['mother_id']
    generation = individual_dict['generation']
    gender = individual_dict['gender']
    timestamp = individual_dict['timestamp']

    cursor.execute("""
        INSERT INTO individuals (id, father_id, mother_id, generation, gender, timestamp, population_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
                   """,
                   (indv_id, father_id, mother_id, generation, gender, timestamp, population_id))
    conn.commit()

    cursor.close()
    conn.close()

    return indv_id

# Inserindo um cariótipo na tabela
def add_karyotype(indv_id, individual_dict):

    conn = sqlite3.connect('fishes.db')
    cursor = conn.cursor()

    karyotype = json.dumps(individual_dict['karyotype'])
    chromosome_origin = json.dumps(individual_dict['chromosome_origin'])
    cutting_points = json.dumps(individual_dict['metadados']['cutting_points'])
    method = individual_dict['metadados']['method']

    cursor.execute("""
        INSERT INTO karyotype (individual_id, karyotype, chromosome_origin, cutting_points, method)
        VALUES (?, ?, ?, ?, ?)
                """,
                (indv_id, karyotype, chromosome_origin, cutting_points, method))
    
    conn.commit()

    last_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return last_id

# Inserindo o indivíduo automaticamente (chamando as funções acima)
def add_full_individual(individual_dict):
    individual = add_individual(individual_dict)
    add_karyotype(individual, individual_dict)

    return print("Individual added!")

# Buscando um indivíduo com o id específico
def get_individual_by_id(indv_id):
    
    conn = sqlite3.connect('fishes.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM individuals WHERE id = ?
        """, (indv_id,))
    individual = cursor.fetchone()

    cursor.execute("""
        SELECT * FROM karyotype WHERE individual_id = ?
        """, (indv_id,))
    karyo_data = cursor.fetchone()

    cursor.close()
    conn.close()

    if individual and karyo_data:
        indv_dict = dict(individual)
        indv_dict['karyotype'] = json.loads(karyo_data['karyotype'])
        indv_dict['chromosome_origin'] = json.loads(karyo_data['chromosome_origin'])
        indv_dict['metadados'] = {
            'cutting_points': json.loads(karyo_data['cutting_points']),
        #    'method': json.loads(karyo_data(['method']))
        }
        return indv_dict
# Buscando todos os indivíduos da tabela
def get_all_individuals(population_id=None):

    conn = sqlite3.connect('fishes.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if population_id:
        cursor.execute("""
            SELECT * FROM individuals WHERE population_id = ?
            """, (population_id,))
    else:
        cursor.execute("""
            SELECT * FROM individuals
            """)
    
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return [dict(row) for row in results]