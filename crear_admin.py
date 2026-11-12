
from werkzeug.security import generate_password_hash
from database import conectar_bd
from getpass import getpass


def crear_administrador():
    nombre = input("Nombre del reclutador: ")
    correo = input("Ingresar correo del reclutador: ")
    password = getpass("Contraseña: ")

    if len(password) < 8 or len(password) > 15:
        print("La contraseña debe tener entre 8 y 15 caracteres")
        return

    conexion = conectar_bd()
    cursor = conexion.cursor()

    try:
        # Verificar si el correo ya existe
        cursor.execute(
            "SELECT id FROM usuarios WHERE correo = %s",
            (correo,)
        )

        existente = cursor.fetchone()

        if existente:
            print("Este correo ya está registrado")
            return

        # Cifrar contraseña
        password_hash = generate_password_hash(password)

        # Registrar reclutador
        sql = """
            INSERT INTO usuarios
            (nombre, correo, password, rol, estado)
            VALUES (%s, %s, %s, 'reclutador', 1)
        """

        cursor.execute(sql, (nombre, correo, password_hash))
        conexion.commit()

        print("Reclutador creado correctamente")

    except Exception as error:
        conexion.rollback()
        print("Error:", error)

    finally:
        cursor.close()
        conexion.close()


if __name__ == "__main__":
    crear_administrador()
