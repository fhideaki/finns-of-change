from app.services.genetics import PopulationManager

def test_create_individual():
    pm = PopulationManager()
    indv = pm.create_individual()
    
    assert 'indv_id' in indv
    assert len(indv['karyotype']) == 6  # 3 pares
    assert isinstance(indv['karyotype'][0], list)