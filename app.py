from flask import Flask, request
from database import conectar_bd

app = Flask(__name__)


@app.route("/probar")
def probar_data():
    conec = conectar_bd()

    if conec.is_connected():
        conec.close()

    return {
        "mensaje": "Conexion ok"
    }


#Actualizar hoja de vida por medio del id
@app.route("/api/actualizarhv/<int:id>", methods=["PUT"])
def actualizarhv(id):

    # Recibir los datos enviados
    datos = request.json()
    conec = conectar_bd()
    cursor = conec.cursor(buffered=True)

    # Verificar que la HV existe
    buscar = """SELECT id FROM hojas_vida WHERE id=%s"""
    cursor.execute(buscar, (id,))
    result = cursor.fetchone()

    if result is None:
        cursor.close()
        conec.close()
        return {
            "Mensaje": "No se encontro la hoja de vida"
        }, 404

    # Verificar que el correo no esté registrado en otra HV
    sqlcorreo = """
        SELECT id
        FROM hojas_vida
        WHERE correo = %s
        AND id != %s
    """

    cursor.execute(sqlcorreo, (datos["correo"], id))
    result = cursor.fetchone()

    if result is not None:
        cursor.close()
        conec.close()
        return {
            "Mensaje": "El correo ya esta registrado con otra hoja de vida"
        }, 400

    # Actualizar
    sqlactualizar = """
        UPDATE hojas_vida
        SET nombre=%s, edad=%s, ciudad=%s, correo=%s,
            fotografia=%s, programa=%s, ficha=%s, jornada=%s
        WHERE id=%s
    """

    valor = (
        datos["nombre"],
        datos["edad"],
        datos["ciudad"],
        datos["correo"],
        datos.get("fotografia"),
        datos["programa"],
        datos["ficha"],
        datos["jornada"],
        id
    )

    cursor.execute(sqlactualizar, valor)
    conec.commit()

    cursor.close()
    conec.close()

    return {
        "Mensaje": "Hoja de vida actualizada",
        "id": id
    }, 200







# Eliminar hoja de vida por id
@app.route("/api/eliminarhv/<int:id>", methods=["DELETE"])
def eliminar_hv(id):
    conec = conectar_bd()
    cursor = conec.cursor()

    cursor.execute("SELECT id FROM hojas_vida WHERE id=%s", (id,))
    existe = cursor.fetchone()

    if existe is None:
        cursor.close()
        conec.close()
        return {"mensaje": "No se encontró la hoja de vida"}, 404

    cursor.execute("DELETE FROM hojas_vida WHERE id=%s", (id,))
    conec.commit()

    cursor.close()
    conec.close()

    return {"mensaje": "Hoja de vida eliminada"}, 200

    



#Consultar hoja de vida por id
@app.route("/api/consultahv/<int:id>", methods=["GET"])
def obtener_hvida(id):
    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    sql = "SELECT * FROM hojas_vida WHERE id = %s"
    cursor.execute(sql, (id,))

    datos = cursor.fetchone()

    cursor.close()
    conec.close()

    if datos is None:
        return {"mensaje": "No se encontró la hoja de vida"}, 404

    return datos, 200






@app.route("/api/registrohv", methods=["POST"])
def registrar_hojavida():

    conec = conectar_bd()
    cursor = conec.cursor()
    datos = request.get_json()

    # Consultar si el correo ya existe en la base de datos
    cursor.execute(
        "SELECT * FROM hojas_vida WHERE correo = %s",
        (datos['correo'],)
    )

    resultado = cursor.fetchone()

    if resultado:
        cursor.close()
        conec.close()

        return {
            "mensaje": "El correo ya está registrado"
        }, 400

    sql = """
        INSERT INTO hojas_vida
        (nombre, edad, ciudad, correo, fotografia, programa, ficha, jornada)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (
        datos['nombre'],
        datos['edad'],
        datos['ciudad'],
        datos['correo'],
        datos['fotografia'],
        datos['programa'],
        datos['ficha'],
        datos['jornada']
    ))

    conec.commit()

    # Obtener el ID generado automáticamente
    id_regenerado = cursor.lastrowid

    cursor.close()
    conec.close()

    return {
        "mensaje": "Registro de hoja de vida",
        "id": id_regenerado
    }, 201


@app.route("/")
def inicio():
    return "Api hoja de vida funcionando"


# BUSCAR UNA HOJA DE VIDA POR ID
@app.route("/api/hojas-vida/<int:id>")
def obtener_hojasvidaid(id):

    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM hojas_vida WHERE id = %s",
        (id,)
    )

    hoja_vida = cursor.fetchone()

    cursor.close()
    conec.close()

    if hoja_vida:
        return hoja_vida

    return {
        "mensaje": "Hoja de vida no encontrada"
    }, 404


# LISTAR TODAS LAS HOJAS DE VIDA
@app.route("/api/hojas-vida")
def obtener_hojasvida():

    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    # Consultar todos los registros de la base de datos
    cursor.execute("SELECT * FROM hojas_vida")

    # Obtener todos los registros
    hojas_vida = cursor.fetchall()

    cursor.close()
    conec.close()

    return hojas_vida




#ESTUDIOS HOJA DE VIDA

#Consultar todos los estudios asociados a una hoja de vida.
@app.route("/api/hojasvida/<int:hoja_vida_id>/estudios", methods=["GET"])
def consultar_estudios(hoja_vida_id):

    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    sql = """
        SELECT id, hoja_vida_id, nivel, institucion, titulo, anio_graduacion
        FROM estudios
        WHERE hoja_vida_id = %s
    """

    cursor.execute(sql, (hoja_vida_id,))

    estudios = cursor.fetchall()

    cursor.close()
    conec.close()

    return estudios, 200


#Registrar un nuevo esstudio 
@app.route("/api/hojasvida/<int:hoja_vida_id>/estudios", methods=["POST"])
def registrar_estudio(hoja_vida_id):

    datos = request.get_json()

    conec = conectar_bd()
    cursor = conec.cursor()

    sql = """
        INSERT INTO estudios
        (hoja_vida_id, nivel, institucion, titulo, anio_graduacion)
        VALUES (%s, %s, %s, %s, %s)
    """

    valores = (
        hoja_vida_id,
        datos["nivel"],
        datos["institucion"],
        datos["titulo"],
        datos["anio_graduacion"]
    )

    cursor.execute(sql, valores)
    conec.commit()

    id_estudio = cursor.lastrowid

    cursor.close()
    conec.close()

    return {
        "mensaje": "Estudio registrado correctamente",
        "id": id_estudio,
        "hoja_vida_id": hoja_vida_id
    }, 201


#Consultar un estudio especifico 
@app.route("/api/estudios/<int:id>", methods=["GET"])
def consultar_estudio(id):

    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    sql = """
        SELECT id, hoja_vida_id, nivel, institucion, titulo, anio_graduacion
        FROM estudios
        WHERE id = %s
    """

    cursor.execute(sql, (id,))

    estudio = cursor.fetchone()

    cursor.close()
    conec.close()

    if estudio is None:
        return {
            "mensaje": "Estudio no encontrado"
        }, 404

    return estudio, 200


#Actualizar un estudio

@app.route("/api/actualizarestudios/<int:id>", methods=["PUT"])
def actualizar_estudio(id):

    datos = request.json()
    conec = conectar_bd()
    cursor = conec.cursor(buffered=True)

    # Verificar si el estudio existe
    buscar = """SELECT id FROM estudios WHERE id=%s"""
    cursor.execute(buscar, (id,))
    result = cursor.fetchone()

    if result is None:
        cursor.close()
        conec.close()
        return {
            "Mensaje": "No se encontro el estudio"
        }, 404

    # Actualizar
    sqlactualizar = """
        UPDATE estudios
        SET nivel=%s,
            institucion=%s,
            titulo=%s,
            anio_graduacion=%s
        WHERE id=%s
    """

    valor = (
        datos["nivel"],
        datos["institucion"],
        datos["titulo"],
        datos["anio_graduacion"],
        id
    )

    cursor.execute(sqlactualizar, valor)
    conec.commit()

    cursor.close()
    conec.close()

    return {
        "Mensaje": "Estudio actualizado",
        "id": id
    }, 200
    
    
    # Eliminar estudio por id
@app.route("/api/eliminarestudio/<int:id>", methods=["DELETE"])
def eliminar_estudio(id):
    conec = conectar_bd()
    cursor = conec.cursor()

    cursor.execute("SELECT id FROM estudios WHERE id=%s", (id,))
    existe = cursor.fetchone()

    if existe is None:
        cursor.close()
        conec.close()
        return {"mensaje": "No se encontró el estudio"}, 404

    cursor.execute("DELETE FROM estudios WHERE id=%s", (id,))
    conec.commit()

    cursor.close()
    conec.close()

    return {"mensaje": "Estudio eliminado"}, 200


#Endpoints experiencia laboral

#Consultar todas las experiencias laborales asociadas a una hoja de vida.

@app.route("/api/hojasvida/<int:hoja_vida_id>/experiencias", methods=["GET"])
def consultar_experiencias(hoja_vida_id):

    conec = conectar_bd()
    cursor = conec.cursor(dictionary=True)

    sql = """
        SELECT id, hoja_vida_id, empresa, cargo, tiempo, funciones
        FROM experiencias
        WHERE hoja_vida_id = %s
    """

    cursor.execute(sql, (hoja_vida_id,))

    experiencias = cursor.fetchall()

    cursor.close()
    conec.close()

    return experiencias, 200



# Registrar una nueva experiencia laboral
@app.route("/api/hojasvida/<int:hoja_vida_id>/experiencias", methods=["POST"])
def registrar_experiencia(hoja_vida_id):

    datos = request.get_json()

    conec = conectar_bd()
    cursor = conec.cursor()

    sql = """
        INSERT INTO experiencias
        (hoja_vida_id, empresa, cargo, tiempo, funciones)
        VALUES (%s, %s, %s, %s, %s)
    """

    valores = (
        hoja_vida_id,
        datos["empresa"],
        datos["cargo"],
        datos["tiempo"],
        datos["funciones"]
    )

    cursor.execute(sql, valores)
    conec.commit()

    id_experiencia = cursor.lastrowid

    cursor.close()
    conec.close()

    return {
        "mensaje": "Experiencia registrada correctamente",
        "id": id_experiencia,
        "hoja_vida_id": hoja_vida_id
    }, 201
    
    
    
    
    # Actualizar una experiencia laboral
@app.route("/api/actualizarexperiencia/<int:id>", methods=["PUT"])
def actualizar_experiencia(id):

    datos = request.json()
    conec = conectar_bd()
    cursor = conec.cursor(buffered=True)

    # Verificar si la experiencia existe
    buscar = """SELECT id FROM experiencias WHERE id=%s"""
    cursor.execute(buscar, (id,))
    result = cursor.fetchone()

    if result is None:
        cursor.close()
        conec.close()
        return {
            "Mensaje": "No se encontro la experiencia"
        }, 404

    # Actualizar
    sqlactualizar = """
        UPDATE experiencias
        SET empresa=%s,
            cargo=%s,
            tiempo=%s,
            funciones=%s
        WHERE id=%s
    """

    valor = (
        datos["empresa"],
        datos["cargo"],
        datos["tiempo"],
        datos["funciones"],
        id
    )

    cursor.execute(sqlactualizar, valor)
    conec.commit()

    cursor.close()
    conec.close()

    return {
        "Mensaje": "Experiencia actualizada",
        "id": id
    }, 200



# Eliminar experiencia por id
@app.route("/api/eliminarexperiencia/<int:id>", methods=["DELETE"])
def eliminar_experiencia(id):

    conec = conectar_bd()
    cursor = conec.cursor()

    cursor.execute(
        "SELECT id FROM experiencias WHERE id=%s",
        (id,)
    )

    existe = cursor.fetchone()

    if existe is None:
        cursor.close()
        conec.close()

        return {
            "mensaje": "No se encontró la experiencia"
        }, 404

    cursor.execute(
        "DELETE FROM experiencias WHERE id=%s",
        (id,)
    )

    conec.commit()

    cursor.close()
    conec.close()

    return {
        "mensaje": "Experiencia eliminada"
    }, 200














if __name__ == "__main__":
    app.run(debug=True)
