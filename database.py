import mysql.connector

def conectar_bd():

    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="hojas_de_vida"
    )

    if conexion.is_connected():
        print("Conectado correctamente")

    return conexion