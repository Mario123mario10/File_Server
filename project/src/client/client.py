import socket
import json
import argparse


def send_request(server_host, server_port, command, path=""):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((server_host, server_port))
        request = json.dumps({'command': command, 'path': path})
        client_socket.send(request.encode())

        response = receive_json_response(client_socket)
        if response["status"] == "error":
            print(response["message"])
        else:
            if command in ['ls', 'tree']:
                if "data" in response:
                    print("\n")
                    print(response["data"])
                else:
                    print("Brak danych do wyświetlenia.")
            elif command == 'get':
                if "size" in response:
                    save_path = input("Podaj nazwę pliku do zapisu (opcjonalnie ze ścieżką): ")
                    receive_file_data(client_socket, save_path, response["size"])
                else:
                    print("Brak danych pliku do pobrania.")


def receive_json_response(client_socket):
    response_data = ''
    while True:
        part = client_socket.recv(4096).decode()
        response_data += part
        if len(part) < 4096:
            break
    return json.loads(response_data)


def receive_file_data(client_socket, save_path, file_size):
    with open(save_path, 'wb') as file:  # binarnie
        received_size = 0
        while received_size < file_size:
            data = client_socket.recv(4096)
            file.write(data)
            received_size += len(data)


def run_client(server_host, server_port):
    while True:
        print("Dostępne komendy: get, ls, tree, exit")
        command = input("Wprowadź komendę: ")

        if command == 'exit':
            break
        elif command in ['ls', 'tree']:
            path = input("Wprowadź ścieżkę: ")
            send_request(server_host, server_port, command, path)
        elif command == 'get':
            path = input("Wprowadź ścieżkę do pliku: ")
            send_request(server_host, server_port, command, path)
        else:
            print("Nieznana komenda.")
        print("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('host', help='Server host')
    parser.add_argument('--port', default=65536, type=int, help='Server port')
    args = parser.parse_args()
    run_client(args.host, args.port)


if __name__ == "__main__":
    main()
