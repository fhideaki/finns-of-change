# Imports
from flask import request, jsonify, Blueprint, redirect
from app.models.individual import GeneReader
from app.services.genetics import PopulationManager
from app.database.operations import *

# Construtor do flask
api = Blueprint('api', __name__)

# Página inicial
@api.route('/')
def status():
    return 'API Working'

# Criando uma população
@api.route('/createpopulation/<name>')
def create_population(name):
    pop = add_population(name)
    return f"Population {pop} named {name} created!"

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

# Buscando as características do indivíduo
@api.route('/individual/<id>/analysis')
def get_analysis(id):
    result = get_individual_characteristics(id)
    return result

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

        add_full_individual(child)
        return jsonify(child)

# Criando populações
@api.route('/populations', methods=['GET','POST'])
def population_route():

    if request.method == 'GET':
        result = get_populations()
        return jsonify(result)
    
    elif request.method == 'POST':
        data = request.get_json()
        data = dict(data)

        name = data['name']
        population = add_population(name)
        return jsonify(population)

@api.route('/statistics')
def get_statistics_dataframe():

    indviduals_dict = build_statistics_dataframe()

    return jsonify(indviduals_dict)