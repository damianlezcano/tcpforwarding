import socket
import ssl
import threading
import argparse

def handle_source_to_target(source_socket, target_socket):
    try:
        while True:
            data = source_socket.recv(4096)
            if not data:
                break
            #print(f"Forwarding data from source to target: {data}")
            target_socket.sendall(data)
    except Exception as e:
        print(f"Error in source to target handler: {e}")
    finally:
        source_socket.close()
        target_socket.close()

def handle_target_to_source(target_socket, source_socket):
    try:
        while True:
            data = target_socket.recv(4096)
            if not data:
                break
            #print(f"Forwarding data from target to source: {data}")
            source_socket.sendall(data)
    except Exception as e:
        print(f"Error in target to source handler: {e}")
    finally:
        target_socket.close()
        source_socket.close()

def accept_connections(server_ssl, handler):
    while True:
        try:
            client_socket, client_addr = server_ssl.accept()
            print(f"Accepted connection from {client_addr}")
            # Iniciar un nuevo hilo para manejar la conexión
            threading.Thread(target=handler, args=(client_socket,)).start()
        except ssl.SSLError as e:
            print(f"SSL Error: {e}")
        except Exception as e:
            print(f"Unexpected Error: {e}")

def start_server(source_port, target_port, certfile, keyfile):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile, keyfile=keyfile)
    
    source_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    source_server.bind(("0.0.0.0", source_port))
    source_server.listen(5)
    print(f"Listening on source port {source_port}...")

    source_server_ssl = context.wrap_socket(source_server, server_side=True)

    target_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    target_server.bind(("0.0.0.0", target_port))
    target_server.listen(5)
    print(f"Listening on target port {target_port}...")

    target_server_ssl = context.wrap_socket(target_server, server_side=True)

    # Iniciar hilos para aceptar conexiones
    threading.Thread(target=accept_connections, args=(source_server_ssl, lambda s: handle_source_connections(s, target_server_ssl))).start()
    threading.Thread(target=accept_connections, args=(target_server_ssl, lambda s: handle_target_connections(s, source_server_ssl))).start()

def handle_source_connections(source_socket, target_server_ssl):
    try:
        # Aceptar conexión en el puerto de destino
        target_socket, _ = target_server_ssl.accept()
        print(f"Accepted connection on target port for source client")
        # Crear hilos para manejar las conexiones bidireccionales
        threading.Thread(target=handle_source_to_target, args=(source_socket, target_socket)).start()
        threading.Thread(target=handle_target_to_source, args=(target_socket, source_socket)).start()
    except Exception as e:
        print(f"Error handling source connections: {e}")
    finally:
        source_socket.close()

def handle_target_connections(target_socket, source_server_ssl):
    try:
        # Aceptar conexión en el puerto de origen
        source_socket, _ = source_server_ssl.accept()
        print(f"Accepted connection on source port for target client")
        # Crear hilos para manejar las conexiones bidireccionales
        threading.Thread(target=handle_source_to_target, args=(source_socket, target_socket)).start()
        threading.Thread(target=handle_target_to_source, args=(target_socket, source_socket)).start()
    except Exception as e:
        print(f"Error handling target connections: {e}")
    finally:
        target_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HTTPS server to forward data bidirectionally between two ports.")
    parser.add_argument("source_port", type=int, help="The port to listen for incoming connections to forward.")
    parser.add_argument("target_port", type=int, help="The port to forward the data to.")
    parser.add_argument("certfile", type=str, help="The path to the SSL certificate file.")
    parser.add_argument("keyfile", type=str, help="The path to the SSL key file.")

    args = parser.parse_args()

    start_server(args.source_port, args.target_port, args.certfile, args.keyfile)
