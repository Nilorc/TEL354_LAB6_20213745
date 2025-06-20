import yaml
import uuid

# ===== Clases base =====
class Alumno:
    def __init__(self, nombre, codigo, mac):
        self.nombre = nombre
        self.codigo = str(codigo)
        self.mac = mac
    def __str__(self):
        return f"{self.codigo} - {self.nombre} ({self.mac})"

class Curso:
    def __init__(self, codigo, estado, nombre, alumnos, servidores):
        self.codigo = codigo
        self.estado = estado
        self.nombre = nombre
        self.alumnos = [str(a) for a in alumnos]
        self.servidores = servidores
    def __str__(self):
        return f"{self.codigo} - {self.nombre} [{self.estado}]"

class Servidor:
    def __init__(self, nombre, ip, servicios):
        self.nombre = nombre
        self.ip = ip
        self.servicios = servicios
    def __str__(self):
        servs = "\n".join([f"  - {s['nombre']} ({s['protocolo']}:{s['puerto']})" for s in self.servicios])
        return f"{self.nombre} ({self.ip})\nServicios:\n{servs}"

# ===== Variables globales =====
alumnos = []
cursos = []
servidores = []
conexiones = []  # formato: dict con handler, alumno, servidor, servicio

# ===== Importar/Exportar YAML =====
def importar_datos():
    entrada = input("Nombre del archivo YAML : ").strip()
    if not entrada.endswith(".yaml"):
        entrada += ".yaml"
    try:
        with open(entrada, 'r') as f:
            data = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Error al importar '{entrada}': {e}")
        return

    alumnos.clear()
    cursos.clear()
    servidores.clear()
    conexiones.clear()

    for a in data.get("alumnos", []):
        alumnos.append(Alumno(**a))
    for c in data.get("cursos", []):
        cursos.append(Curso(c['codigo'], c['estado'], c['nombre'], c['alumnos'], c['servidores']))
    for s in data.get("servidores", []):
        servidores.append(Servidor(s['nombre'], s['ip'], s['servicios']))

    print(f"✔ Datos importados correctamente desde '{entrada}'.")

def exportar_datos():
    path = input("Nombre del archivo de salida : ").strip()
    if not path.endswith(".yaml"):
        path += ".yaml"
    data = {
        'alumnos': [vars(a) for a in alumnos],
        'cursos': [{
            'codigo': c.codigo,
            'estado': c.estado,
            'nombre': c.nombre,
            'alumnos': c.alumnos,
            'servidores': c.servidores
        } for c in cursos],
        'servidores': [vars(s) for s in servidores]
    }
    try:
        with open(path, 'w') as f:
            yaml.dump(data, f)
        print(f"✔ Datos exportados correctamente a '{path}'.")
    except Exception as e:
        print(f"❌ Error al exportar: {e}")

# ===== Submenú Alumnos =====
def menu_alumnos():
    while True:
        print("\n--- SUBMENÚ ALUMNOS ---")
        print("1) Listar todos los alumnos")
        print("2) Ver detalle de un alumno")
        print("3) Eliminar un alumno")
        print("4) Volver")
        op = input(">> ")
        if op == '1':
            if not alumnos:
                print("No hay alumnos cargados.")
            else:
                for a in alumnos:
                    print(a)
        elif op == '2':
            codigo = input("Código del alumno: ")
            encontrado = False
            for a in alumnos:
                if a.codigo == codigo:
                    print(f"Nombre: {a.nombre}\nCódigo: {a.codigo}\nMAC: {a.mac}")
                    encontrado = True
                    break
            if not encontrado:
                print("❌ Alumno no encontrado.")
        elif op == '3':
            codigo = input("Código del alumno a eliminar: ")
            for i, a in enumerate(alumnos):
                if a.codigo == codigo:
                    alumnos.pop(i)
                    print("✔ Alumno eliminado.")
                    break
            else:
                print("❌ Alumno no encontrado.")
        elif op == '4':
            break
        else:
            print("Opción inválida.")

# ===== Submenú Cursos =====
def menu_cursos():
    while True:
        print("\n--- SUBMENÚ CURSOS ---")
        print("1) Listar todos los cursos")
        print("2) Ver detalle de un curso")
        print("3) Agregar/eliminar alumno en curso")
        print("4) Volver")
        op = input(">> ")
        if op == '1':
            if not cursos:
                print("No hay cursos cargados.")
            else:
                for c in cursos:
                    print(c)
        elif op == '2':
            codigo = input("Código del curso: ")
            for c in cursos:
                if c.codigo == codigo:
                    print(f"\nCurso: {c.nombre}")
                    print(f"Estado: {c.estado}")
                    print(f"Alumnos: {', '.join(c.alumnos)}")
                    print("Servidores permitidos:")
                    for s in c.servidores:
                        print(f"  - {s['nombre']}: {', '.join(s['servicios_permitidos'])}")
                    break
            else:
                print("❌ Curso no encontrado.")
        elif op == '3':
            codigo = input("Código del curso: ")
            for c in cursos:
                if c.codigo == codigo:
                    print("1) Agregar alumno\n2) Eliminar alumno")
                    ac = input("Elija: ")
                    if ac == '1':
                        nuevo = input("Código del alumno a agregar: ")
                        if nuevo not in c.alumnos:
                            c.alumnos.append(nuevo)
                            print("✔ Alumno agregado.")
                        else:
                            print("Ya estaba inscrito.")
                    elif ac == '2':
                        borrar = input("Código del alumno a eliminar: ")
                        if borrar in c.alumnos:
                            c.alumnos.remove(borrar)
                            print("✔ Alumno eliminado del curso.")
                        else:
                            print("No estaba inscrito.")
                    break
            else:
                print("❌ Curso no encontrado.")
        elif op == '4':
            break
        else:
            print("Opción inválida.")

# ===== Submenú Servidores =====
def menu_servidores():
    while True:
        print("\n--- SUBMENÚ SERVIDORES ---")
        print("1) Listar todos los servidores")
        print("2) Ver detalle de un servidor")
        print("3) Volver")
        op = input(">> ")
        if op == '1':
            if not servidores:
                print("No hay servidores cargados.")
            else:
                for s in servidores:
                    print(s)
                    print("-" * 40)
        elif op == '2':
            nombre = input("Nombre del servidor: ")
            for s in servidores:
                if s.nombre.lower() == nombre.lower():
                    print(s)
                    break
            else:
                print("❌ Servidor no encontrado.")
        elif op == '3':
            break
        else:
            print("Opción inválida.")

# ===== Submenú Conexiones =====
def alumno_puede_conectarse(cod_alumno, servidor, servicio):
    # Verifica si alumno está en algún curso DICTANDO, donde el servidor y servicio están permitidos
    for c in cursos:
        if c.estado != "DICTANDO":
            continue
        if cod_alumno not in c.alumnos:
            continue
        for s in c.servidores:
            if s['nombre'] == servidor:
                if servicio in s['servicios_permitidos']:
                    return True
    return False

def menu_conexiones():
    while True:
        print("\n--- SUBMENÚ CONEXIONES ---")
        print("1) Crear conexión")
        print("2) Listar conexiones")
        print("3) Eliminar conexión")
        print("4) Volver")
        op = input(">> ")
        if op == '1':
            cod_alumno = input("Código del alumno: ")
            nombre_servidor = input("Nombre del servidor: ")
            nombre_servicio = input("Nombre del servicio: ")
            # Validar alumno y servidor
            if not any(a.codigo == cod_alumno for a in alumnos):
                print("❌ Alumno no existe.")
                continue
            if not any(s.nombre == nombre_servidor for s in servidores):
                print("❌ Servidor no existe.")
                continue
            if not alumno_puede_conectarse(cod_alumno, nombre_servidor, nombre_servicio):
                print("⛔ Alumno NO autorizado para ese servicio en ese servidor.")
                continue
            handler = str(uuid.uuid4())[:8]
            conexiones.append({'handler': handler, 'alumno': cod_alumno, 'servidor': nombre_servidor, 'servicio': nombre_servicio})
            print(f"✔ Conexión creada. Handler: {handler}")
        elif op == '2':
            if not conexiones:
                print("No hay conexiones creadas.")
            else:
                for c in conexiones:
                    print(f"Handler: {c['handler']}, Alumno: {c['alumno']}, Servidor: {c['servidor']}, Servicio: {c['servicio']}")
        elif op == '3':
            handler = input("Handler de la conexión a eliminar: ")
            for i, c in enumerate(conexiones):
                if c['handler'] == handler:
                    conexiones.pop(i)
                    print("✔ Conexión eliminada.")
                    break
            else:
                print("No se encontró el handler.")
        elif op == '4':
            break
        else:
            print("Opción inválida.")

# ===== Banner principal =====
def mostrar_menu():
    print(r"""
  _   _      _                      _              ____  _     __  __ 
 | \ | | ___| |___      _____  _ __| | _____ _ __ |  _ \| |   |  \/  |
 |  \| |/ _ \ __\ \ /\ / / _ \| '__| |/ / _ \ '__|| |_) | |   | |\/| |
 | |\  |  __/ |_ \ V  V / (_) | |  |   <  __/ |   |  __/| |___| |  | |
 |_| \_|\___|\__| \_/\_/ \___/|_|  |_|\_\___|_|   |_|   |_____|_|  |_|

         Network Policy Manager - UPSM
    """)
    print("1) Importar")
    print("2) Exportar")
    print("3) Cursos")
    print("4) Alumnos")
    print("5) Servidores")
    print("6) Políticas")
    print("7) Conexiones")
    print("8) Salir")

def main():
    while True:
        mostrar_menu()
        op = input(">>> ")

        if op == '1':
            importar_datos()
        elif op == '2':
            exportar_datos()
        elif op == '3':
            menu_cursos()
        elif op == '4':
            menu_alumnos()
        elif op == '5':
            menu_servidores()
        elif op == '6':
            print("(No requerido por la guía, omitiendo submenú de políticas)")
        elif op == '7':
            menu_conexiones()
        elif op == '8':
            print("Saliendo del programa.")
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main()
