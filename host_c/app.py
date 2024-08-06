import socket
import ssl
import threading
import argparse

def forward_data(source, destination):
    try:
        while True:
            data = source.recv(4096)
            if not data:
                break
            destination.sendall(data)
    finally:
        source.close()
        destination.close()

def forward_traffic(remote_host, remote_port, local_port, client_cert, client_key):
    try:
        # Crear contexto SSL adecuado para el cliente
        context = ssl.create_default_context()
        context.load_cert_chain(certfile=client_cert, keyfile=client_key)  # Cargar certificado del cliente y clave privada
        context.check_hostname = False  # Ignorar la verificación del nombre del host
        context.verify_mode = ssl.CERT_NONE  # No verificar el certificado del servidor
        
        # Conectar al host remoto usando SSL
        raw_remote_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_remote_conn = context.wrap_socket(raw_remote_conn, server_hostname=remote_host)
        ssl_remote_conn.connect((remote_host, remote_port))
        print(f'Connected to remote host {remote_host}:{remote_port} with SSL (certificates provided)')
    except ssl.SSLError as e:
        print(f"SSL error: {e}")
        exit(1)
    except socket.error as e:
        print(f"Socket error: {e}")
        exit(1)

    try:
        # Conectar al puerto local
        local_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        local_conn.connect(('127.0.0.1', local_port))
        print(f'Connected to local port {local_port}')
    except socket.error as e:
        print(f"Socket error: {e}")
        exit(1)

    # Crear hilos para manejar el forwarding bidireccional
    threading.Thread(target=forward_data, args=(ssl_remote_conn, local_conn)).start()
    threading.Thread(target=forward_data, args=(local_conn, ssl_remote_conn)).start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Forward TCP traffic between a remote host and a local port using SSL/TLS.')
    
    parser.add_argument('remote_host', type=str, help='Remote host to connect to.')
    parser.add_argument('remote_port', type=int, help='Remote port to connect to.')
    parser.add_argument('local_port', type=int, help='Local port to forward traffic to.')
    parser.add_argument('client_cert', type=str, help='Path to the client certificate file.')
    parser.add_argument('client_key', type=str, help='Path to the client key file.')

    args = parser.parse_args()

    forward_traffic(args.remote_host, args.remote_port, args.local_port, args.client_cert, args.client_key)
