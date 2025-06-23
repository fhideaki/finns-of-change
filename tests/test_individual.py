from app.models.individual import GeneReader
from app.services.genetics import PopulationManager

def test_gene_reader_characteristics():
    pm = PopulationManager()
    indv = pm.create_individual()
    reader = GeneReader(indv)

    codons = reader.get_codons()
    amino = reader.get_aminoacids(codons)
    color = reader.get_color(amino)
    speed = reader.get_swimming_speed(amino)

    assert isinstance(color, str)
    assert isinstance(speed, int)
    assert indv['gender'] in ['male','female']
