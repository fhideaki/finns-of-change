# Imports
from flask import Flask, request, jsonify, Blueprint
from app.models.individual import GeneReader
from app.services.genetics import PopulationManager
from app.database.operations import *

# Construtor do flask
api = Blueprint('api', __name__)

# Página inicial
@api.route('/')
def status():
    return 'API Working'

# Criando um indivíduo
@api.route('/create')
def create():
    # Criando uma instância de PopulationManager
    pop_mngr = PopulationManager()
    # Criando um indivíduo com a instância criada
    individual = pop_mngr.create_individual()
    # Passando o indivíduo como parâmetro
    g_reader = GeneReader(individual)

    codon_list = g_reader.get_codons()
    aminoacids = g_reader.get_aminoacids(codon_list)
    gender = g_reader.get_gender(aminoacids)

    individual['gender'] = gender

    add_full_individual(individual)
    
    return jsonify(individual)

# Listando indivíduos
@api.route('/list/<int:population_id>')
def list_individuals(population_id):
    result = get_all_individuals(population_id)
    return jsonify(result)

# Listando todos os indivíduos
@api.route('/list')
def list_all_individuals():
    result = get_all_individuals()
    return jsonify(result)

# Buscando um indivíduo específico
@api.route('/individual/<id>')
def get_individual(id):
    result = get_individual_by_id(id)
    return jsonify(result)

# Criando indivíduos a partir de outros (fecundação)
@api.route('/cross', methods=['GET','POST'])
def fertilize():

    if request.method == 'GET':
        return jsonify({"message": "Use POST method with JSON payload"}), 400
     
    elif request.method == 'POST':
        pop_mngr = PopulationManager()

        data = request.get_json()
        data = dict(data)

        father_id = data['father_id']
        mother_id = data['mother_id']

        father = get_individual_by_id(father_id)
        father_karyo = get_karyotype_by_id(father_id)

        father.update(father_karyo)

        mother = get_individual_by_id(mother_id)
        mother_karyo = get_karyotype_by_id(mother_id)
        mother.update(mother_karyo)

        if father['gender'] == mother['gender']:
            return jsonify({'error': 'Same gender fertilization is not possible'}), 400
        
        child = pop_mngr.fertilization(father, mother)

        # add_full_individual(child)
        return jsonify(child)