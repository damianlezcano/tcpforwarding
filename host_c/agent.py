import socket
import threading
import sys

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

def forward_traffic(remote_host, remote_port, local_port):
    # Conectar al host remoto
    remote_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_conn.connect((remote_host, remote_port))
    print(f'Connected to remote host {remote_host}:{remote_port}')
    
    # Conectar al puerto local
    local_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_conn.connect(('127.0.0.1', local_port))
    print(f'Connected to local port {local_port}')

    # Crear hilos para manejar el forwarding bidireccional
    threading.Thread(target=forward_data, args=(remote_conn, local_conn)).start()
    threading.Thread(target=forward_data, args=(local_conn, remote_conn)).start()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <remote_host> <remote_port> <local_port>")
        sys.exit(1)

    remote_host = sys.argv[1]
    remote_port = int(sys.argv[2])
    local_port = int(sys.argv[3])

    forward_traffic(remote_host, remote_port, local_port)
