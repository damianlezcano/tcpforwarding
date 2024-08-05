import socket
import threading
import argparse

# Función para manejar la conexión en un puerto y reenviar datos al otro
def handle_source_to_target(source_socket, target_socket):
    try:
        while True:
            data = source_socket.recv(4096)
            if not data:
                break
            print(f"Forwarding data from source to target: {data}")
            target_socket.sendall(data)
    except Exception as e:
        print(f"Error in source to target handler: {e}")
    finally:
        source_socket.close()

def handle_target_to_source(target_socket, source_socket):
    try:
        while True:
            data = target_socket.recv(4096)
            if not data:
                break
            print(f"Forwarding data from target to source: {data}")
            source_socket.sendall(data)
    except Exception as e:
        print(f"Error in target to source handler: {e}")
    finally:
        target_socket.close()

def start_server(source_port, target_port):
    # Configurar el socket para el puerto de origen
    source_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    source_server.bind(("0.0.0.0", source_port))
    source_server.listen(5)
    print(f"Listening on source port {source_port}...")

    # Configurar el socket para el puerto de destino
    target_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    target_server.bind(("0.0.0.0", target_port))
    target_server.listen(5)
    print(f"Listening on target port {target_port}...")

    while True:
        # Aceptar conexión en el puerto de origen
        source_socket, source_addr = source_server.accept()
        print(f"Accepted connection on source port from {source_addr}")

        # Aceptar conexión en el puerto de destino
        target_socket, target_addr = target_server.accept()
        print(f"Accepted connection on target port from {target_addr}")

        # Crear hilos para manejar las conexiones bidireccionales
        source_to_target_thread = threading.Thread(target=handle_source_to_target, args=(source_socket, target_socket))
        target_to_source_thread = threading.Thread(target=handle_target_to_source, args=(target_socket, source_socket))
        
        source_to_target_thread.start()
        target_to_source_thread.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TCP server to forward data bidirectionally between two ports.")
    parser.add_argument("source_port", type=int, help="The port to listen for incoming connections to forward.")
    parser.add_argument("target_port", type=int, help="The port to forward the data to.")

    args = parser.parse_args()

    start_server(args.source_port, args.target_port)

