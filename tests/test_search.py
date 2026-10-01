from app.search import buscar_por_codigo


def test_buscar_codigo_unico():
    resultados = buscar_por_codigo("HO-21251")

    assert len(resultados) == 1
    assert resultados[0]["codigo"] == "HO-21251"
    assert resultados[0]["zona"] == "FC7"


def test_buscar_codigo_em_duas_localizacoes():
    resultados = buscar_por_codigo("HO-20987")

    assert len(resultados) == 2

    zonas = {resultado["zona"] for resultado in resultados}

    assert zonas == {"C5", "CART"}


def test_busca_aceita_codigo_sem_hifen():
    resultados = buscar_por_codigo("HO20987")

    assert len(resultados) == 2
