import socket
import ssl
import argparse
import threading

def handle_client(local_socket, remote_socket):
    def relay(source, destination):
        while True:
            data = source.recv(4096)
            if not data:
                break
            destination.sendall(data)

    # Crear hilos para manejar la comunicación en ambas direcciones
    local_to_remote_thread = threading.Thread(target=relay, args=(local_socket, remote_socket))
    remote_to_local_thread = threading.Thread(target=relay, args=(remote_socket, local_socket))

    local_to_remote_thread.start()
    remote_to_local_thread.start()

    # Esperar a que ambos hilos terminen
    local_to_remote_thread.join()
    remote_to_local_thread.join()

    local_socket.close()
    remote_socket.close()

def start_proxy(local_port, remote_host, remote_port, certfile, keyfile):
    # Crear el contexto SSL para cliente
    context = ssl.create_default_context()
    context.load_cert_chain(certfile, keyfile)
    context.check_hostname = False  # Ignorar la verificación del nombre del host
    context.verify_mode = ssl.CERT_NONE  # No verificar el certificado del servidor

    # Configurar el socket local
    local_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_server.bind(('0.0.0.0', local_port))
    local_server.listen(5)

    print(f'Listening on port {local_port} and forwarding to {remote_host}:{remote_port}')

    while True:
        local_socket, _ = local_server.accept()

        # Crear el socket remoto y establecer la conexión
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((remote_host, remote_port))

        # Envolver el socket remoto con SSL
        remote_socket = context.wrap_socket(remote_socket, server_hostname=remote_host)

        # Manejar la transferencia de datos en un hilo separado
        client_thread = threading.Thread(target=handle_client, args=(local_socket, remote_socket))
        client_thread.start()

def main():
    parser = argparse.ArgumentParser(description='TCP Proxy with SSL forwarding')
    parser.add_argument('local_port', type=int, help='Local port to listen on')
    parser.add_argument('remote_host', help='Remote host to forward to')
    parser.add_argument('remote_port', type=int, help='Remote port to forward to')
    parser.add_argument('certfile', help='Path to SSL certificate file')
    parser.add_argument('keyfile', help='Path to SSL key file')

    args = parser.parse_args()

    start_proxy(args.local_port, args.remote_host, args.remote_port, args.certfile, args.keyfile)

if __name__ == '__main__':
    main()