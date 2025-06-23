# Imports
import random
import uuid
from datetime import datetime
from app.models.individual import GeneReader

# Classe Nucleo - Armazena e manipula a sequência genética
class Nucleus():
    
    def __init__(self, karyotype = None):
        # O cariótipo de um indivíduo vai armazenar 4 pares de cromossomos 2n = 8.
        # Cada par é formado por um cromossomo vindo do pai e outro cromossomo vindo da mãe.
        # O cariótipo então é o conjunto dos pares. Precisa ter 8 elementos (4 pares de cromossomos).
        if karyotype == None:
            self.karyotype = []
        else:
            self.karyotype = karyotype
        self.nucleotides = [x for x in range(4)]
        
    def create_dna(self):
        # Método para criar DNA. Deve ser usado somente para a primeira geração de indivíduos.
        self.karyotype = [
            [x for x in random.choices(self.nucleotides, k=30)]
            for i in range(6)
        ]
    
    def __get_chromosome_pair(self, karyotype):
        # Método para agrupar os cromossomos homólogos.
        # Cromossomos homólogos = mesma posição, mesmo tamanho e com genes em posições correspondentes.
        self.chromosome_pairs = list(zip(karyotype[::2],karyotype[1::2]))
        return self.chromosome_pairs
    
    def __crossing_over(self, chromosome_pair, cutting_point):
        new_chromosome = [ x for x in chromosome_pair[0][0:cutting_point] + chromosome_pair[1][cutting_point:]]
        return new_chromosome
    
    def do_meiosis(self, cutting_points=None):
        # Método para executar a meiose, 1 célula diploide (2n = 8) tem que gerar 4 células haploides (n = 4).
        haploids = []
        
        # Trazendo a lista de cromossomos para a função
        pairs = self.__get_chromosome_pair(self.karyotype)
              
        from_father = []
        from_mother = []
        mixeds_1 = []
        mixeds_2 = []    
        
        if cutting_points == None:
            cutting_points = []
            for pair in pairs:
                cutting_points.append(random.randrange(len(pair[0])))
            
        index = 0

        
        for pair in pairs:
            
            from_father.append(pair[0])
            from_mother.append(pair[1])
            
            mixed1 = self.__crossing_over(pair, cutting_points[index])
            mixeds_1.append(mixed1)
            mixed2 = self.__crossing_over(pair[::-1], cutting_points[index])
            mixeds_2.append(mixed2)
            
            index += 1
        
        haploids.append({
            'origin':'father',
            'cutting_points':[],
            'chromosomes':from_father
        })
        haploids.append({
            'origin':'mother',
            'cutting_points':[],
            'chromosomes':from_mother
        })
        
        index = 0
        
        haploids.append({
            'origin':'mixed',
            'cutting_points':cutting_points, 
            'chromosomes':mixeds_1
        })
        
        haploids.append({
            'origin':'mixed',
            'cutting_points':cutting_points, 
            'chromosomes':mixeds_2
        })
            
        return haploids
    
    def to_dict(self):
        return {
            'karyotype':self.karyotype,
            'number_of_chromosomes':sum(len(pair['chromosomes']) for pair in self.karyotype),
            'mixed_count':sum(1 for pair in self.karyotype if pair['mixed']=='yes')
        }
    
    
# Criando uma classe que vai gerenciar a população
class PopulationManager():
    
    # Armazenando o contador e os IDs de todos os integrantes da população
    def __init__(self):
        self.population_counter = 0
        self.population = []
        
    # Método fertilization() que pede dois objetos Nucleus() e cria um indivíduo.
    def fertilization(self, father, mother):
        
        generation = 0
        
        generation_father = father['generation']
        generation_mother = mother['generation']
        
        generation = max(generation_father,generation_mother) + 1
        
        # Cria núcleos a partir de objetos
        nucleus_father = Nucleus(karyotype=father['karyotype'])
        nucleus_mother = Nucleus(karyotype=mother['karyotype'])
        
        # Executa a meiose dos dois objetos e armazena nas variáveis
        fat_gametes = nucleus_father.do_meiosis()
        mot_gametes = nucleus_mother.do_meiosis()

        # Escolhe um par de cromossomos por conjunto de gametas para formar um indivíduo
        fat_gamete = random.choice(fat_gametes)
        mot_gamete = random.choice(mot_gametes)

        # Cria o cariótipo do indivíduo novo
        #karyotype = list(zip(fat_gamete['chromosomes'],mot_gamete['chromosomes']))
        index = 0
        karyotype = []
        for i in fat_gamete['chromosomes']:
            karyotype.append(fat_gamete['chromosomes'][index])
            karyotype.append(mot_gamete['chromosomes'][index])
            index += 1
        
        # Retorna um dicionário com as informações do novo indivíduo
        new_individual = {
            'indv_id':str(uuid.uuid4()), 
            'father_id':father['indv_id'],
            'mother_id':mother['indv_id'],
            'generation':generation,
            'karyotype':karyotype,
            'chromosome_origin':{'father_gamete':fat_gamete['origin'],'mother_gamete':mot_gamete['origin']},
            'timestamp':datetime.now().isoformat(),
            'metadados':{
                'cutting_points':{
            'father': fat_gamete['cutting_points'],
            'mother': mot_gamete['cutting_points']
        },
                'method':'meiosis'
            }
        }

        # Gênero
        reader = GeneReader(new_individual)
        codons = reader.get_codons()
        aminoacids = reader.get_aminoacids(codons)
        gender = reader.get_gender(aminoacids)
        new_individual['gender'] = gender

        self.population_counter += 1
        self.population.append(new_individual)
        
        return new_individual
        
        
    # Método para criar indivíduos que não vão ter pais
    def create_individual(self):
        
        # Criando uma instância da classe Nucleus()
        nucleus = Nucleus()
        nucleus.create_dna()
        
        # Geração 0
        generation = 0

        # Cria o dicionário do novo indivíduo
        new_individual = {
            'indv_id':str(uuid.uuid4()), 
            'father_id':None,
            'mother_id':None,
            'generation':generation,
            'karyotype':nucleus.karyotype,
            'chromosome_origin':None,
            'timestamp':datetime.now().isoformat(),
            'metadados':{
                'cutting_points':None,
                'method':'create_dna'
            }
        }

        # Gênero
        reader = GeneReader(new_individual)
        codons = reader.get_codons()
        aminoacids = reader.get_aminoacids(codons)
        gender = reader.get_gender(aminoacids)
        new_individual['gender'] = gender

        self.population_counter += 1
        self.population.append(new_individual)
        
        return new_individual
