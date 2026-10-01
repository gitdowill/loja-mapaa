from flask import Blueprint, jsonify

from .search import buscar_por_codigo


api = Blueprint("api", __name__, url_prefix="/api")


@api.get("/buscar/<codigo>")
def buscar(codigo):
    resultados = buscar_por_codigo(codigo)

    return jsonify(
        {
            "codigo": codigo,
            "total": len(resultados),
            "resultados": resultados,
        }
    )
