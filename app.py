#instalar flask
from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

DATA_FILE = "vuelos.json"

# Crea una función cargar_datos() que:
def cargar_datos():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Función auxiliar: guardar datos  
def guardar_datos(datos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

@app.route("/", methods=["GET"])
def inicio():
    #jsonify tiene un conjunto como parametro({})
    return jsonify({"mensaje":"API para vuelos"})

@app.route("/api/vuelos", methods=["GET"])
def listar_vuelos():
    datos = cargar_datos()
    for dato in datos:
        dato["destino"] = dato["destino"].title()
    return jsonify(datos)

@app.route("/api/vuelos/<int:vuelo_id>", methods=["GET"])
def obtener_vuelo(vuelo_id):
    datos = cargar_datos()
    for vuelo in datos:
        vuelo["destino"] = vuelo["destino"].title()
        if vuelo["id"] == vuelo_id:
            return jsonify(vuelo) #vuelo?
    return jsonify({"error":"Vuelo no encontrado"}), 404

@app.route("/api/vuelos", methods=["POST"])
def agregar_vuelo():
    #pedir una request? con json que es una funciin, request.get_json()
    nuevo_vuelo = request.get_json()
    #validar con un getter
    if not nuevo_vuelo.get("destino"):
        #retornar en jsonfy
        return jsonify({"error": "El campo 'destino' es obligatorio"}), 400
    #usar los datos
    #se va a cargar en la ultima posición
    datos = cargar_datos()
    if datos:
        nuevo_vuelo["id"] = datos[-1]["id"] + 1
    else:
        nuevo_vuelo["id"] = 1
    #nuevo_vuelo["id"] = datos[-1]["id"] + 1 if datos else 1
    
    nuevo_vuelo["capacidad"] = int(nuevo_vuelo["capacidad"])
    nuevo_vuelo["vendidos"] = int(nuevo_vuelo["vendidos"])
    nuevo_vuelo["destino"] = nuevo_vuelo["destino"].lower()
    
    if not nuevo_vuelo["capacidad"]:
        nuevo_vuelo["capacidad"] = int(nuevo_vuelo["capacidad": 100])
    if not nuevo_vuelo["vendidos"]:
        nuevo_vuelo["vendidos"] = int(nuevo_vuelo["vendidos": 0])
        
    #agregar a la lista
    datos.append(nuevo_vuelo)
    guardar_datos(datos)
    return jsonify(nuevo_vuelo), 201

# Consigna 5:
@app.route("/api/vuelos/<int:vuelo_id>", methods=["PUT"])
def actualizar_vuelo(vuelo_id):
    vuelo_dato = request.get_json()
    datos = cargar_datos()
    
    #buscar los id
    for vuelo in datos:
        if vuelo["id"] == vuelo_id:
            vuelo.update({ #lleva coma porque es un diccionario
                "destino" : vuelo_dato.get("destino", vuelo["destino"]),
                "capacidad" : int(vuelo_dato.get("capacidad", vuelo["capacidad"])),
                "vendidos" : int(vuelo_dato.get("vendidos", vuelo["vendidos"]))
            })
            vuelo["destino"] = vuelo["destino"].title()
            guardar_datos(datos)
            return jsonify(vuelo)
    return jsonify({"error": "Vuelo no encontrado"}), 404

# Consigna 6:
@app.route("/api/vuelos/<int:vuelo_id>", methods=["DELETE"])
def eliminar_vuelo(vuelo_id):
    datos = cargar_datos()
    nuevos_datos = [vuelo for vuelo in datos if vuelo["id"] != vuelo_id]
    
    if len(nuevos_datos) == len(datos):
        return jsonify({"error": "Vuelo no encontrado"}), 404
    elif len(nuevos_datos) != len(datos):
        guardar_datos(nuevos_datos)
        
    return jsonify({"mensaje": f"Vuelo {vuelo_id} eliminado correctamente"})


# Consigna 7:
# Crear un endpoint POST /vender que:
# 1. Obtenga los datos JSON de la petición.
# El campo id del vuelo se envía en el body del request, por ejemplo:
# {
#   "id": 1
# }
# Tips: en Flask se obtiene así:
# datos = request.get_json()
# vuelo_id = datos.get("id")
# 2. Cargue todos los vuelos existentes.
# 3. Busque el vuelo por su id.
# 4. Si no lo encuentra, devuelva {"error": "Vuelo no encontrado"} con código 404.
# 5. Verifique que vendidos < capacidad:
#   - Si hay lugar disponible, incremente "vendidos" en 1.
#   - Si el vuelo está completo (vendidos >= capacidad), devuelva {"error": "Vuelo completo"} con código 400.
# 6. Guarde los datos actualizados.
# 7. Devuelva el vuelo actualizado en formato JSON.
@app.route("/api/vender", methods=["POST"])
def vender_vuelo():
    #obtener datos
    datos = request.get_json()
    vuelo_id = datos.get("id")
    cargar_datos(datos)
    for vuelo in datos:
        if vuelo["id"] == vuelo_id:
            return jsonify(vuelo_id)
        else:
            return jsonify({"error" : "Vuelo no encontrado"}), 404
    for vuelo in datos:
        if vuelo["vendidos"] <= vuelo["capacidad"]:
            vuelo["vendidos"] += 1
        elif vuelo["vendidos"] >= vuelo["capacidad"]:
            return jsonify({"error": "Vuelo completo"}), 400
    guardar_datos(datos)
    return jsonify(vuelo)

if __name__ == "__main__":
    if not os.path.exists(DATA_FILE):
        guardar_datos([])
    app.run(debug=True)