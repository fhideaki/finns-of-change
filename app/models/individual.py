
from app.utils.support import inverted_aminoacid_table

# Classe GeneReader, que vai receber o DNA e exibir as características de acordo com os genes gerados.
class GeneReader():
    
    def __init__(self, individual_dictionary):
        self.karyotype = individual_dictionary['karyotype']
        self.color = None
        self.swimming_speed = 0
        self.gender = None
    
    def get_codons(self):
        codon_list = []
        for chromo in self.karyotype:
            new_list = []
            for i in range(0, len(chromo), 3):
                codon = chromo[i:i+3]
                if len(codon) == 3:
                    new_list.append(tuple(chromo[i:i+3]))
            codon_list.append(new_list)
        return codon_list

    def get_aminoacids(self, codon_list):
        aminoacids = []

        for chromo in codon_list:
            amino = []
            for codon in chromo:
                amino.append(inverted_aminoacid_table.get(codon, 'unknown'))
            aminoacids.append(amino)

        return aminoacids
    
    # Agora consigo analisar cada par de cromossomos.
    def get_color(self, aminoacids):
        
    # Vou definir arbitrariamente que o primeiro par define a cor.
    # A cor geralmente é definida pela quantidade de melanina, que é sintetizada pela tirosina (tyrosine)
        color_chromosomes = aminoacids[0] + aminoacids[1]
        color_gene = {x: color_chromosomes.count(x) for x in set(color_chromosomes)}

        r = color_gene.get('tyrosine', 0) * 100
        if r > 255:
            r = 255
        g = color_gene.get('histidine', 0) * 100
        if g > 255:
            g = 255
        b = color_gene.get('alanine', 0) * 100
        if b > 255:
            b = 255
        
        self.color = f"{r:02x}{g:02x}{b:02x}"

        return self.color
    
    def get_swimming_speed(self, aminoacids):
    # Definindo arbitrariamente que a velocidade de nado está associada com o segundo par de cromossomos.
        swim_chromosomes = aminoacids[2] + aminoacids[3]
        swim_gene = {x: swim_chromosomes.count(x) for x in set(swim_chromosomes)}
        self.swimming_speed = 1 * (swim_gene.get('arginine',0) * 5) - swim_gene.get('stop',0)
    
        return self.swimming_speed
    
    def get_gender(self, aminoacids, index=5):
    # Definindo arbitrariamente o gênero do peixe
        gender_chromosomes = aminoacids[index]
        gender_gene = {x: gender_chromosomes.count(x) for x in set(gender_chromosomes)}
        glutamine = gender_gene.get('glutamine',0)
        
        if glutamine > 1:
            self.gender = 'male'
        else:
            self.gender = 'female'

        return self.gender

