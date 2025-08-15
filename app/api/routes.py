# Imports
from flask import request, jsonify, Blueprint, redirect, render_template, url_for, flash, send_file
from app.models.individual import GeneReader
from app.services.genetics import PopulationManager
from app.database.operations import *
from collections import Counter
import io
import random

# Construtor do flask/ Flask constructor
api = Blueprint('api', __name__)

# Página inicial/ Home page
@api.route('/', endpoint='index')
def status():
    # Obtendo a população definida pelo usuário, por padrão será 'all'
    # Getting the population defined by the user, the standard is 'all'
    standard_population = request.args.get('population', 0)
    population_name = "All Populations"

    # Criando a lista de populações
    # Creating population list
    population_list = get_populations()

    # Retornando todos os indivíduos do banco de dados
    # Returning every individual from database
    all_individuals_raw = build_statistics_dataframe()

    # Filtrando o que vai ser exibido conforme selecionado pelo usuário
    # Filtering what is going to be shown according to what the user selected
    individuals_to_display = []

    if standard_population == 0:
        individuals_to_display = all_individuals_raw
        population_name = "All Populations"
    
    else:
        try:
            standard_population = int(standard_population)
                
            individuals_to_display = [
                indv for indv in all_individuals_raw 
                if indv.get('population_id') == standard_population
            ]

            for i in population_list:
                if i['id'] == standard_population:
                    population_name = i['name']
                    break

        except ValueError:
            individuals_to_display = all_individuals_raw
            standard_population = 0

    # Total de populações
    # Total populations
    total_populations = len(population_list)

    total_fishes = len(individuals_to_display)

    avg_speed = 0
    mf_ratio = {'male':0, 'female':0}
    colors_for_chart = []
    generations_list = []

    if total_fishes > 0:
        for i in individuals_to_display:
            avg_speed += i.get('swimming_speed',0)
            colors_for_chart.append('#' + i.get('color', 'FFFFFF'))
            if i.get('gender') == 'female':
                mf_ratio['female'] += 1
            elif i.get('gender') == 'male':
                mf_ratio['male'] += 1
            generations_list.append(int(i.get('generation',0)))
        
        avg_speed = round(avg_speed/total_fishes, 2)
        generations = max(generations_list or [1])
    else:
        avg_speed = 0
        generations = 0
    
    # Contagem da ocorrência das cores
    # Color occurrences counting
    color_counts = Counter(colors_for_chart)

    # Ordering the colors just like the chromatic circles
    sorted_color_items = sorted(color_counts.items(), key= lambda item: hex_to_hsv(item[0])[0])

    color_distribution = dict(sorted_color_items)

    return render_template('index.html',
                           standard_population=standard_population,
                           all_populations_data=population_list,
                           population_name=population_name,
                           total_populations=total_populations,
                           total_fishes=total_fishes,
                           avg_speed=avg_speed,
                           generations=generations,
                           color_data=color_distribution,
                           sex_data=mf_ratio,
                           individuals=individuals_to_display)

# Criando uma população/ Creating a population
@api.route('/createpopulation/<name>', methods=['POST'])
def create_population(name):
    name = request.form.get('name')
    add_population(name)
    return redirect('/populations')

# Criando um indivíduo/ Creating an individual
@api.route('/create', methods=['POST'])
def create_individuals():
    if request.method == 'POST':
        try:
            # Pegando os dados do formulário
            # Getting the forms data
            population_id = int(request.form['population_id'])
            # Quantidade de indivíduos que serão criados
            quantity = int(request.form['quantity'])

            # Lista dos indivíduos criados
            created_individuals = []

            for i in range(quantity):
                pop_mngr = PopulationManager()

                individual = pop_mngr.create_individual(population_id=population_id)
                g_reader = GeneReader(individual)

                codon_list = g_reader.get_codons()
                aminoacids = g_reader.get_aminoacids(codon_list)
                gender = g_reader.get_gender(aminoacids)

                individual['gender'] = gender

                add_full_individual(individual, population_id)

                created_individuals.append(individual)

            # Adicionando uma mensagem de sucesso para o usuário
            flash(f"{quantity} individual(s) created successfully for Population ID {population_id}", 'success')

            # Redirecionando para a página daquela população específica
            return redirect(url_for('api.list', population_id=population_id))
    
        except KeyError as e:
            flash(f"Missing form data: {e}. Please ensure 'population_id' and 'quantity' are submitted.", 'error')
            return redirect(request.referrer or url_for('api.index')) # Volta para a página anterior ou index
        except ValueError:
            flash("Invalid input for population ID or quantity. Please provide valid numbers.", 'error')
            return redirect(request.referrer or url_for('api.index'))
        except Exception as e:
            flash(f"An error occurred during individual creation: {e}", 'error')
            return redirect(request.referrer or url_for('api.index'))
        
    return redirect(url_for('api.index'))

# Listando indivíduos
@api.route('/list/<int:population_id>')
def list_individuals(population_id):

    all_individuals = build_statistics_dataframe()

    selected_individuals = []

    for i in all_individuals:
        if i['population_id'] == population_id:
            selected_individuals.append(i)     

    populations_list = get_populations()

    for i in populations_list:
        if i['id'] == population_id:
            population_name = i['name']

    return render_template('population.html', 
                           population_id=population_id,
                           all_populations_data = populations_list,
                           population_name=population_name,
                           individuals_data=selected_individuals)

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

    fish = get_individual_by_id(id)
    family_tree = get_family_tree(id, max_depth=3)
    fish_karyo = get_karyotype_by_id(id)
    fish_char = get_individual_characteristics(id)

    populations_list = get_populations()

    for i in populations_list:
        if i['id'] == fish['population_id']:
            population_name = i['name']

    return render_template('fish.html',
                           fish_id=id,
                           father_id=fish['father_id'],
                           mother_id=fish['mother_id'],
                           generation=fish['generation'],
                           gender=fish['gender'],
                           timestamp=fish['timestamp'],
                           population_id=fish['population_id'],
                           population_name=population_name,
                           karyotype=fish_karyo['karyotype'],
                           chromosome_origin=fish_karyo['chromosome_origin'],
                           cutting_points=fish_karyo['cutting_points'],
                           method=fish_karyo['method'],
                           color=fish_char['color'],
                           swimming_speed=fish_char['swimming_speed'],
                           genes=fish_char['genes'],
                           family_tree_data=family_tree
                           )

# Função auxiliar para a árvore genealógica
def get_family_tree(individual_id, depth=0, max_depth=3):
    
    if depth >= max_depth:
        return None
    
    individual = get_individual_by_id(individual_id)
    if not individual:
        return None
    
    # Montando o indivíduo
    tree_node = {
        'id':individual['id'],
        'gender':individual['gender'],
        'generation':individual['generation'],
        'color': get_individual_characteristics(individual['id'])['color'],
        'parents':[]
    }

    # Buscando o pai e os pais dos pais e etc
    if individual.get('father_id'):
        father_tree = get_family_tree(individual['father_id'], depth + 1, max_depth)
        if father_tree:
            tree_node['parents'].append(father_tree)

    # Buscando a mãe e as mães das mães e etc
    if individual.get('mother_id'):
        mother_tree = get_family_tree(individual['mother_id'], depth + 1, max_depth)
        if father_tree:
            tree_node['parents'].append(mother_tree)

    return tree_node

# Rota para fertilizar
@api.route('/fertilize/<int:population_id>', methods=['GET', 'POST'])
def fertilize(population_id):
    if request.method == 'GET':
        # Salvando todos os indivíduos
        all_individuals = build_statistics_dataframe()

        individuals_data = []

        # Filtrando por população
        for i in all_individuals:
            if i['population_id'] == population_id:
                individuals_data.append(i)
        
        all_populations_data = get_populations()

        female_individuals = [i for i in individuals_data if i['gender'] == 'female']
        male_individuals = [i for i in individuals_data if i['gender'] == 'male']

        for pop in all_populations_data:
            if pop['id'] == population_id:
                population_name = pop['name']

        return render_template('fertilize.html',
                               female_individuals=female_individuals,
                               male_individuals=male_individuals,
                               population_id=population_id,
                               population_name=population_name,
                               all_populations_data=all_populations_data)
    
    if request.method == 'POST':

        female_id = request.form.get('female_id')
        male_id = request.form.get('male_id')

        pop_mngr = PopulationManager()

        all_individuals = build_statistics_dataframe()

        mother = next((i for i in all_individuals if i['id'] == female_id), None)
        father = next((i for i in all_individuals if i['id'] == male_id), None)

        new_individual = pop_mngr.fertilization(father, mother)

        new_individual['population_id'] = population_id

        add_full_individual(new_individual, population_id)

        return redirect(url_for('api.fertilize', population_id=population_id))

# Rota para fertilizar n vezes
@api.route('/massfertilization', methods=['POST'])
def mass_fertilization():
    try:
        # Pegando os dados do formulário
        population_id = int(request.form['population_id'])

        # Quantidade de indivíduos que serão criados
        quantity = int(request.form['quantity'])

        pop_mngr = PopulationManager()

        created_individuals = []

        all_individuals = build_statistics_dataframe()

        individuals_data = []
        
        # Filtrando por população
        for i in all_individuals:
            if i['population_id'] == population_id:
                individuals_data.append(i)
            
        female_individuals = [i for i in individuals_data if i['gender'] == 'female']
        male_individuals = [i for i in individuals_data if i['gender'] == 'male']

        # Loop para fecundações
        for i in range(quantity):
            mother = random.choice(female_individuals)
            father = random.choice(male_individuals)

            new_individual = pop_mngr.fertilization(father, mother)

            new_individual['population_id'] = population_id

            add_full_individual(new_individual, population_id)

            created_individuals.append(new_individual)
        
        all_populations_data = get_populations()

        for pop in all_populations_data:
            if pop['id'] == population_id:
                population_name = pop['name']

        return render_template('fertilize.html',
                               female_individuals=female_individuals,
                               male_individuals=male_individuals,
                               population_id=population_id,
                               population_name=population_name,
                               all_populations_data=all_populations_data)
    except KeyError as e:
        flash(f"Missing form data: {e}. Please ensure 'population_id' and 'quantity' are submitted.", 'error')
        return redirect(request.referrer or url_for('api.index')) # Volta para a página anterior ou index
    except ValueError:
        flash("Invalid input for population ID or quantity. Please provide valid numbers.", 'error')
        return redirect(request.referrer or url_for('api.index'))
    except Exception as e:
        flash(f"An error occurred during individual creation: {e}", 'error')
        return redirect(request.referrer or url_for('api.index'))
            
# Rota para fertilizar n vezes
@api.route('/selectedfertilization', methods=['POST'])
def selected_fertilization():
    try:
        if request.method == 'POST':
            # Pegando os dados do formulário
            population_id = int(request.form['population_id'])

            # Quantidade de indivíduos que serão criados
            quantity = int(request.form['quantity'])

            # Pegando os IDs dos peixes selecionados
            selected_female_ids = request.form.getlist('selected_female_fishes[]')
            selected_male_ids = request.form.getlist('selected_male_fishes[]')

            # Verificando se pelo menos um peixe de cada gênero foi selecionado
            if not selected_female_ids or not selected_male_ids:
                flash("Please, select at least one female and one male fish for the selected fecundation.", 'error')
                return redirect(request.referrer or url_for('api.index'))

            all_individuals = [
                i for i in build_statistics_dataframe()
                if i['population_id'] == population_id
            ]

            selected_females = [
                ind for ind in all_individuals 
                if str(ind['id']) in selected_female_ids
                ]
            
            selected_males = [
                ind for ind in all_individuals 
                if str(ind['id']) in selected_male_ids
                ]

            pop_mngr = PopulationManager()
            
            # Loop para fecundações
            for i in range(quantity):
                mother = random.choice(selected_females)
                father = random.choice(selected_males)

                new_individual = pop_mngr.fertilization(father, mother)
                new_individual['population_id'] = population_id

                add_full_individual(new_individual, population_id)
            
            flash(f"{quantity} new individuals were successfully created in population '{population_id} - {population_name}'.", 'success')

            individuals_data = [
                i for i in all_individuals
                if i['population_id'] == population_id
            ]

            female_individuals = [
                i for i in individuals_data 
                if i['gender'] == 'female'
                ]
            male_individuals = [
                i for i in individuals_data 
                if i['gender'] == 'male'
                ]
            
            all_populations_data = get_populations()

            for pop in all_populations_data:
                if pop['id'] == population_id:
                    population_name = pop['name']

            return render_template('fertilize.html',
                                female_individuals=female_individuals,
                                male_individuals=male_individuals,
                                population_id=population_id,
                                population_name=population_name,
                                all_populations_data=all_populations_data)
    
    except KeyError as e:
        flash(f"Missing form data: {e}. Please ensure 'population_id' and 'quantity' are submitted.", 'error')
        return redirect(request.referrer or url_for('api.index')) # Volta para a página anterior ou index
    except ValueError:
        flash("Invalid input for population ID or quantity. Please provide valid numbers.", 'error')
        return redirect(request.referrer or url_for('api.index'))
    except Exception as e:
        flash(f"An error occurred during individual creation: {e}", 'error')
        return redirect(request.referrer or url_for('api.index'))
            
# Criando populações
@api.route('/populations', methods=['GET','POST'])
def population_route():

    if request.method == 'GET':
        result = get_populations()
        return render_template('create_population.html', populations=result)
    
    elif request.method == 'POST':
        name = request.form['name']
        add_population(name)
        return redirect('/populations')

# Retornando um JSON com todas as estatísticas dos peixes criados
@api.route('/statistics')
def get_statistics_dataframe():

    indviduals_dict = build_statistics_dataframe()

    return jsonify(indviduals_dict)

# Deletando um indivíduo
@api.route('/delete/<id>', methods=['POST'])
def delete_individual_route(id):
    
    delete_individual(id)
    
    return redirect(request.referrer or url_for('api.index'))

# Deletando vários indivíduos
@api.route('/delete_individuals', methods=['POST'])
def delete_individuals_route():

    individuals_to_delete = request.args.getlist('selected_fishes')
    for i in individuals_to_delete:
        delete_individual(i)

    return redirect(request.referrer or url_for('api.index'))

# Deletando uma população
@api.route('/delete/population/<population_id>', methods=['POST'])
def delete_population_route(population_id):
    
    delete_population(population_id)

    return redirect('/populations')

# Exportando JSON
@api.route('/export_json', methods=['GET'])
def export_json():
    # Recebendo os IDs das populações selecionadas
    selected_population_ids_str = request.args.getlist('selected_populations')

    # Convertendo para inteiros
    selected_population_ids = [int(pop_id) for pop_id in selected_population_ids_str if pop_id.isdigit()]

    if not selected_population_ids:
        flash("No population selected for exportation.", 'warning')
        return redirect(request.referrer)
    
    all_data = build_statistics_dataframe()

    data_to_export = [item for item in all_data if item.get('population_id') in selected_population_ids]


    json_output = json.dumps(data_to_export, indent=4)
    buffer = io.BytesIO()
    buffer.write(json_output.encode('utf-8'))
    buffer.seek(0)

    # Enviando o arquivo JSON para o navegador
    return send_file(
        buffer,
        mimetype='application/json',
        as_attachment=True,
        download_name='finns_of_change_export.json'
    )