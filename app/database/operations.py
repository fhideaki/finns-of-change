# Imports
import sqlite3
import json
from app.models.individual import GeneReader
from flask import jsonify
# import pandas as pd

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
def add_individual(individual_dict, population_id):

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
        INSERT INTO karyotype (id, karyotype, chromosome_origin, cutting_points, method)
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

# Buscando um indivíduo com o id específico
def get_individual_by_id(indv_id):
    
    conn = sqlite3.connect('fishes.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM individuals WHERE id = ?
        """, (indv_id,))
    
    individual = cursor.fetchone()
    
    cursor.close()
    conn.close()

    return dict(individual)

def get_karyotype_by_id(indv_id):
    
    conn = sqlite3.connect('fishes.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM karyotype WHERE id = ?
        """, (indv_id,))
    
    karyo_data = cursor.fetchone()
    
    karyo_dict = {}
    
    karyo_dict['id'] = karyo_data['id']
    karyo_dict['karyotype'] = json.loads(karyo_data['karyotype'])
    karyo_dict['chromosome_origin'] = json.loads(karyo_data['chromosome_origin'])
    karyo_dict['cutting_points'] = json.loads(karyo_data['cutting_points'])
    karyo_dict['method'] = karyo_data['method']
    

    cursor.close()
    conn.close()
    
    return karyo_dict

# Buscando as características individuais e também os genes
def get_individual_characteristics(id):
    data = {'indv_id':id}
    indv_id = data['indv_id']
    indv = get_individual_by_id(indv_id)
    indv = dict(indv)
    indv_karyo = get_karyotype_by_id(indv_id)
    indv_karyo = dict(indv_karyo)
    indv.update(indv_karyo)
    g_reader = GeneReader(indv)
    codon_list = g_reader.get_codons()
    aminoacids = g_reader.get_aminoacids(codon_list)
    color = g_reader.get_color(aminoacids)
    speed = g_reader.get_swimming_speed(aminoacids)
    result = {
        'color':color,
        'swimming_speed':speed,
        'genes':aminoacids
    }
    return result

# Buscando todas as populações da tabela
def get_populations():

    conn = sqlite3.connect('fishes.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM population
        """)
        
    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return [dict(row) for row in results]

# Buscando todas as informações para retornar um DataFrame
def build_statistics_dataframe():

    individuals_dict = get_all_individuals()

    dict_for_dataframe = []
    
    for i in individuals_dict:
        dict(i)
        id = i['id']
        karyo = get_karyotype_by_id(id)
        characteristics = get_individual_characteristics(id)
        i.update(karyo)
        i.update(characteristics)

        if i['chromosome_origin'] == None:
            chromosome_origin_father = None
            chromosome_origin_mother = None
            cutting_points_father = None
            cutting_points_mother = None
        else:
            chromosome_origin_father = i['chromosome_origin']['father_gamete']
            chromosome_origin_mother = i['chromosome_origin']['mother_gamete']
            cutting_points_father = i['cutting_points']['father']
            cutting_points_mother = i['cutting_points']['mother']

        individual = {
            'id': i['id'],
            'father_id':i['father_id'],
            'mother_id':i['mother_id'],
            'generation':i['generation'],
            'population_id':i['population_id'],
            'chromosome_origin_father': chromosome_origin_father,
            'chromosome_origin_mother': chromosome_origin_mother,
            'cutting_points_father': cutting_points_father,
            'cutting_points_mother': cutting_points_mother,
            'gender': i['gender'],
            'color': i['color'],
            'swimming_speed': i['swimming_speed'],
            'method': i['method'],
            'karyotype_pair_1': i['karyotype'][0:2],
            'karyotype_pair_2': i['karyotype'][2:4],
            'karyotype_pair_3': i['karyotype'][4:6],
            'timestamp':i['timestamp']

        }
        dict_for_dataframe.append(individual)
    return dict_for_dataframe

# Deletando um indivíduo da tabela (e também o cariótipo)
def delete_individual(id):
    conn = sqlite3.connect('fishes.db')
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM karyotype WHERE id = ?
""", (id,))
    
    cursor.execute("""
        DELETE FROM individuals WHERE id = ?
""", (id,))

    conn.commit()

    if cursor.rowcount == 0:
        return jsonify({'message':'Individual not found'}), 404
    else:
        return jsonify({'message':'Individual deleted'}), 200
    
# Deletando uma população inteira
def delete_population(population_id):
    conn = sqlite3.connect('fishes.db')
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM karyotype 
        WHERE id IN (
            SELECT id FROM individuals WHERE population_id = ?
        )
""", (population_id,))
    
    cursor.execute("""
        DELETE FROM individuals
        WHERE population_id = ?
""", (population_id,))
    
    cursor.execute("""
        DELETE FROM population 
        WHERE id = ?
""", (population_id,))
    
    conn.commit()

    if cursor.rowcount == 0:
        return jsonify({'message':'Population not found'}), 404
    else:
        return jsonify({'message':'Population deleted'}), 200
    
    