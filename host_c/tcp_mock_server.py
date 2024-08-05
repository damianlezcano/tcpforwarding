import socket
import argparse

def main(host, port):
    # Crear un socket TCP/IP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Asociar el socket con la dirección y el puerto
        s.bind((host, port))
        s.listen()  # Escuchar conexiones entrantes
        print(f'Esperando conexiones en {host}:{port}')
        
        while True:
            # Aceptar una conexión
            conn, addr = s.accept()
            with conn:
                print(f'Conectado por {addr}')
                while True:
                    # Recibir datos del cliente
                    data = conn.recv(1024)
                    if not data:
                        break
                    print(f'Mensaje recibido: {data.decode()}')
                    
                    # Enviar una respuesta al cliente
                    response = 'Mensaje recibido'.encode()
                    conn.sendall(response)

if __name__ == '__main__':
    # Configurar el análisis de argumentos
    parser = argparse.ArgumentParser(description='Servidor TCP que acepta conexiones, recibe y envía mensajes.')
    parser.add_argument('host', type=str, help='La dirección IP en la que el servidor escuchará')
    parser.add_argument('port', type=int, help='El puerto en el que el servidor escuchará')
    
    args = parser.parse_args()
    
    # Ejecutar la función principal con los parámetros proporcionados
    main(args.host, args.port)
