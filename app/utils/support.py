# Imports
import itertools

# 3 Nucleotídeos == 1 Códon. 
# 1 códon gera aminoácidos. 
# Aminoácidos unidos geram proteínas. 
# Proteínas definem as características do ser.

# Criando uma tabela com as possíveis combinações de nucleotídeos que vão gerar códons diferentes.
codon_table = [x for x in itertools.product([0,1,2,3],repeat=3)]

# Tabela de códons RNA.
# 0 = Adenosina
# 1 = Guanina
# 2 = Citosina
# 3 = Timina

aminoacid_table = {
    'alanine':[(1,2,3),(1,2,2),(1,2,0),(1,2,1)],
    'arginine':[(2,1,3),(2,1,2),(2,1,0),(2,1,1),(0,1,0),(0,1,1)],
    'asparagine':[(0,0,3),(0,0,2)],
    'aspartic_acid':[(1,0,3),(1,0,2)],
    'cysteine':[(3,1,3),(3,1,2)],
    'glutamine':[(2,0,0),(2,0,1)],
    'glutamic_acid':[(1,0,0),(1,0,1)],
    'glycine':[(1,1,3),(1,1,2),(1,1,0),(1,1,1)],
    'histidine':[(2,0,3),(2,0,2)],
    'start':[(0,3,1),(2,3,1),(3,3,1)],
    'isoleucine':[(0,3,3),(0,3,2),(0,3,0)],
    'leucine':[(2,3,3),(2,3,2),(2,3,0),(2,3,1),(3,3,0),(3,3,1)],
    'lysine':[(0,0,0),(0,0,1)],
    'phenylalanine':[(3,3,3),(3,3,2)],
    'proline':[(2,2,3),(2,2,2),(2,2,0),(2,2,1)],
    'serine':[(3,2,3),(3,2,2),(3,2,0),(3,2,1),(0,1,3),(0,1,2)],
    'threonine':[(0,2,3),(0,2,2),(0,2,0),(0,2,1)],
    'tryptophan':[(3,1,1)],
    'tyrosine':[(3,0,3),(3,0,2)],
    'valine':[(1,3,3),(1,3,2),(1,3,0),(1,3,1)],
    'stop':[(3,0,0),(3,1,0),(3,0,1)]
}

inverted_aminoacid_table = {}

for key in aminoacid_table.keys():
    for codon in aminoacid_table[key]:
        inverted_aminoacid_table.update({codon:key})