import yaml
import uuid
import requests

CONTROLLER_HOST = "10.20.12.53"
CONTROLLER_PORT = 8080
FLOODLIGHT_URL = f"http://{CONTROLLER_HOST}:{CONTROLLER_PORT}"

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

# ===== insertar y eliminar flows =====
def push_flow(flow):
    url = f"{FLOODLIGHT_URL}/wm/staticflowpusher/json"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=flow, headers=headers)
        if response.status_code == 200:
            print("✔ Flow instalado en Floodlight.")
        else:
            print(f"❌ Error al instalar flow: {response.text}")
    except Exception as e:
        print(f"❌ No se pudo conectar a Floodlight: {e}")

def delete_flow(flow_name):
    url = f"{FLOODLIGHT_URL}/wm/staticflowpusher/json"
    data = {"name": flow_name}
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.delete(url, json=data, headers=headers)
        if response.status_code == 200:
            print("✔ Flow eliminado de Floodlight.")
        else:
            print(f"❌ Error al eliminar flow: {response.text}")
    except Exception as e:
        print(f"❌ No se pudo conectar a Floodlight: {e}")


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
            # Listar todos los cursos
            if not cursos:
                print("No hay cursos cargados.")
            else:
                print("\n--- Lista de Todos los Cursos ---")
                for c in cursos:
                    print(f"{c.codigo} - {c.nombre} [{c.estado}]")

        elif op == '2':
            # Mostrar detalle de un curso
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
            # Agregar o eliminar alumno en curso
            codigo = input("Código del curso: ")
            for c in cursos:
                if c.codigo == codigo:
                    # Mini leyenda de que solo se pueden agregar alumnos en cursos activos (DICTANDO)
                    if c.estado != "DICTANDO":
                        print("⚠️ Solo se pueden agregar alumnos a cursos con estado 'DICTANDO'.")
                        continue
                    
                    print("1) Agregar alumno\n2) Eliminar alumno")
                    ac = input("Elija: ")
                    if ac == '1':
                        nuevo = input("Código del alumno a agregar: ")
                        if nuevo not in c.alumnos:
                            c.alumnos.append(nuevo)
                            # Buscar el nombre del alumno para la confirmación
                            alumno = next((a for a in alumnos if a.codigo == nuevo), None)
                            if alumno:
                                print(f"✔ Alumno {alumno.nombre} agregado al curso {c.nombre}.")
                            else:
                                print("❌ Alumno no encontrado.")
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
            break  # Volver al menú principal
        else:
            print("❌ Opción inválida.")


# ===== Submenú Alumnos =====
def menu_alumnos():
    while True:
        print("\n--- SUBMENÚ ALUMNOS ---")
        print("1) Crear alumno")  # Opción para crear alumno directamente en el menú
        print("2) Listar alumnos")
        print("3) Ver detalle de un alumno")
        print("4) Eliminar un alumno")
        print("5) Volver")
        op = input(">> ")

        if op == '1':
            # Crear un nuevo alumno directamente en el menú
            nombre = input("Nombre del alumno: ")
            codigo = input("Código del alumno: ")
            mac = input("MAC del alumno (ej. 00:11:22:33:44:55): ")

            # Crear el nuevo alumno y agregarlo a la lista
            nuevo_alumno = Alumno(nombre, codigo, mac)
            alumnos.append(nuevo_alumno)  # Agregar el nuevo alumno a la lista de alumnos
            print(f"✔ Alumno {nombre} agregado correctamente con código {codigo} y MAC {mac}.")

        elif op == '2':
            # Submenú de Listar Alumnos
            print("\n--- SUBMENÚ LISTAR ALUMNOS ---")
            print("1) Listar todos los alumnos")
            print("2) Listar alumnos por curso")
            sub_op = input(">> ")

            if sub_op == '1':
                # Listar todos los alumnos
                if not alumnos:
                    print("No hay alumnos cargados.")
                else:
                    print("\n--- Lista de Todos los Alumnos ---")
                    for a in alumnos:
                        print(a)  # Imprime el string que devuelve el método __str__ de Alumno
            
            elif sub_op == '2':
                # Listar alumnos por curso
                curso_codigo = input("Ingrese el código del curso (ej. TEL354): ").strip()
                alumnos_en_curso = []
                curso_nombre = ""
                for curso in cursos:
                    if curso.codigo == curso_codigo:
                        curso_nombre = curso.nombre
                        for alumno_codigo in curso.alumnos:
                            for a in alumnos:
                                if a.codigo == alumno_codigo:
                                    alumnos_en_curso.append(a)
                        break  # Salir del ciclo si encontramos el curso
                if alumnos_en_curso:
                    print(f"\n--- Alumnos en el curso {curso_codigo} - {curso_nombre} ---")
                    for alumno in alumnos_en_curso:
                        print(alumno)
                else:
                    print(f"❌ No se encontraron alumnos en el curso {curso_codigo}.")
        
        elif op == '3':
            # Ver detalle de un alumno
            codigo = input("Código del alumno: ")
            encontrado = False
            for a in alumnos:
                if a.codigo == codigo:
                    print(f"Nombre: {a.nombre}\nCódigo: {a.codigo}\nMAC: {a.mac}")
                    encontrado = True
                    break
            if not encontrado:
                print("❌ Alumno no encontrado.")
        
        elif op == '4':
            # Eliminar un alumno
            codigo = input("Código del alumno a eliminar: ")
            for i, a in enumerate(alumnos):
                if a.codigo == codigo:
                    alumnos.pop(i)
                    print("✔ Alumno eliminado.")
                    break
            else:
                print("❌ Alumno no encontrado.")
        
        elif op == '5':
            break  # Volver al menú principal
        else:
            print("❌ Opción inválida.")

# ===== Submenú Servidores =====
def menu_servidores():
    while True:
        print("\n--- SUBMENÚ SERVIDORES ---")
        print("1) Listar servidores")
        print("2) Ver detalle de un servidor")
        print("3) Consultar acceso a servicios en un servidor")  # Opción para consultar acceso a servicios
        print("4) Volver")
        op = input(">> ")

        if op == '1':
            # Listar únicamente los nombres de los servidores
            if not servidores:
                print("No hay servidores cargados.")
            else:
                print("\n--- Lista de Servidores ---")
                for s in servidores:
                    print(s.nombre)  # Solo muestra el nombre del servidor
        
        elif op == '2':
            # Ver detalles completos de un servidor
            nombre = input("Nombre del servidor: ")
            for s in servidores:
                if s.nombre.lower() == nombre.lower():
                    print(f"\n--- Detalles del Servidor {s.nombre} ---")
                    print(f"Nombre: {s.nombre}")
                    print(f"IP: {s.ip}")
                    for servicio in s.servicios:
                        print(f"  - {servicio['nombre']} ({servicio['protocolo']}:{servicio['puerto']})")
                    break
            else:
                print("❌ Servidor no encontrado.")

        elif op == '3':
            # Consultar acceso a servicios en un servidor
            print("\n--- CONSULTAR ACCESO A SERVICIOS ---")
            nombre_servidor = input("Ingrese el nombre del servidor: ").strip()
            servicio = input("Ingrese el nombre del servicio (ej. ssh, http, ftp): ").strip()
            cursos_con_acceso = []
            for curso in cursos:
                for servidor in curso.servidores:
                    if servidor['nombre'] == nombre_servidor and servicio in servidor['servicios_permitidos']:
                        cursos_con_acceso.append(curso)

            if cursos_con_acceso:
                print(f"Cursos con acceso al servicio {servicio} en el servidor {nombre_servidor}:")
                for c in cursos_con_acceso:
                    print(f"{c.codigo} - {c.nombre}")
            else:
                print(f"❌ No se encontraron cursos con acceso al servicio {servicio} en el servidor {nombre_servidor}.")

        elif op == '4':
            break  # Volver al menú principal
        else:
            print("❌ Opción inválida.")


# ===== Submenú Conexiones =====
def alumno_puede_conectarse(cod_alumno, servidor, servicio):
    """
    Verifica si un alumno tiene acceso al servicio de un servidor
    según los cursos y servicios permitidos.
    """
    for curso in cursos:
        if curso.estado != "DICTANDO":
            continue  # Solo permite acceso a cursos activos
        if cod_alumno not in curso.alumnos:
            continue  # El alumno no está en este curso
        for s in curso.servidores:
            if s['nombre'] == servidor:
                if servicio in s['servicios_permitidos']:
                    return True  # El alumno tiene acceso al servicio
    print(f"❌ El alumno {cod_alumno} no tiene acceso al servicio {servicio} en el servidor {servidor}.")
    return False  # El alumno no está autorizado



def build_arp_flow(handler, dpid, ip_src, ip_dst, out_port, sentido="arp"):
    """
    Flow para permitir ARP entre hosts.
    """
    flow = {
        "switch": dpid,
        "name": f"{handler}_{sentido}",
        "priority": "32769",  # Priorizamos ARP
        "eth_type": "0x0806",  # ARP
        "arp_spa": ip_src,  # IP de origen
        "arp_tpa": ip_dst,  # IP de destino
        "active": "true",
        "actions": f"output={out_port}"  # Acción de salida
    }
    return flow

def build_flow(handler, dpid, mac_src, ip_src, mac_dst, ip_dst, tcp_port, out_port, sentido="fw"):
    """
    Construye un flow para tráfico de L3 (IP) y L4 (TCP/UDP).
    """
    flow = {
        "switch": dpid,  # DPID del switch
        "name": f"{handler}_{sentido}",  # Flow name (handler + dirección)
        "priority": "32768",  # Prioridad del flow
        "eth_type": "0x0800",  # Tipo de Ethernet: IPv4
        "ipv4_src": ip_src,  # Dirección IP de origen
        "ipv4_dst": ip_dst,  # Dirección IP de destino
        "ip_proto": "0x06",  # Protocolo: TCP
        "tcp_dst": tcp_port,  # Puerto TCP de destino (puede cambiar según servicio)
        "active": "true",  # Flow activo
        "actions": f"output={out_port}"  # Acción: salida por el puerto
    }
    return flow

def get_route(src_dpid, src_port, dst_dpid, dst_port):
    """
    Función simulada para obtener una ruta entre dos dispositivos en la red SDN.
    Debe devolver una lista de switches y puertos (dpid y port) entre el origen y el destino.
    """
    # Aquí llamarías a la API de Floodlight o usarías un algoritmo de enrutamiento
    # Esto es solo un ejemplo
    route = [
        {'dpid': src_dpid, 'port': src_port},
        {'dpid': dst_dpid, 'port': dst_port}
    ]
    return route


def menu_conexiones():
    while True:
        print("\n--- SUBMENÚ CONEXIONES ---")
        print("1) Crear conexión")
        print("2) Listar conexiones")
        print("3) Eliminar conexión")
        print("4) Volver")
        op = input(">> ")

        if op == '1':
            # Pedir información del alumno, servidor y servicio
            cod_alumno = input("Código del alumno: ")
            nombre_servidor = input("Nombre del servidor: ")
            nombre_servicio = input("Nombre del servicio: ")

            # Validar si el alumno tiene acceso al servicio
            if not alumno_puede_conectarse(cod_alumno, nombre_servidor, nombre_servicio):
                print("⛔ Alumno NO autorizado para este servicio.")
                continue

            # Asignar un handler único para la conexión
            handler = str(uuid.uuid4())[:8]
            conexiones.append({'handler': handler, 'alumno': cod_alumno, 'servidor': nombre_servidor, 'servicio': nombre_servicio})
            print(f"✔ Conexión creada. Handler: {handler}")

            # Obtener los datos necesarios para los flows
            ip_servidor = next(s.ip for s in servidores if s.nombre == nombre_servidor)
            mac_alumno = next(a.mac for a in alumnos if a.codigo == cod_alumno)

            # Solicitar DPID y puerto de salida
            dpid = input("Ingrese el DPID del switch conectado al servidor : ")
            out_port = input("Ingrese el puerto de salida para el servidor: ")

            puerto_servicio = 23 if nombre_servicio == "ssh" else 80  # Asumir puerto SSH o HTTP

            # Crear el flow de alumno a servidor (forwarding)
            flow_fw = build_flow(handler, dpid, mac_alumno, ip_servidor, mac_alumno, ip_servidor, puerto_servicio, out_port, sentido="fw")
            push_flow(flow_fw)
            print(f"✔ Flow de Forwarding instalado: {flow_fw['name']}")

            # Crear el flow de servidor a alumno (reverse flow)
            flow_bw = build_flow(handler, dpid, mac_alumno, ip_servidor, mac_alumno, ip_servidor, puerto_servicio, 1, sentido="bw")
            push_flow(flow_bw)
            print(f"✔ Flow de Reverse instalado: {flow_bw['name']}")

            # Flujos ARP (para resolución de IPs)
            flow_arp_fw = build_arp_flow(handler, dpid, ip_servidor, ip_servidor, out_port, sentido="arp_fw")
            push_flow(flow_arp_fw)
            print(f"✔ Flow ARP Forward instalado: {flow_arp_fw['name']}")

            flow_arp_bw = build_arp_flow(handler, dpid, ip_servidor, ip_servidor, 1, sentido="arp_bw")
            push_flow(flow_arp_bw)
            print(f"✔ Flow ARP Reverse instalado: {flow_arp_bw['name']}")

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
                    # Eliminar los flows correspondientes en Floodlight
                    delete_flow(f"{handler}_fw")
                    delete_flow(f"{handler}_bw")
                    delete_flow(f"{handler}_arp_fw")
                    delete_flow(f"{handler}_arp_bw")

                    # Eliminar la conexión de la lista
                    conexiones.pop(i)
                    print("✔ Conexión eliminada y flows removidos.")
                    break
            else:
                print("❌ No se encontró el handler.")

        elif op == '4':
            break  # Volver al menú principal

        else:
            print("❌ Opción inválida.")

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
