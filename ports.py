import socket

def find_free_ports(count=4):
    free_ports = []
    for i in range(count):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            free_ports.append(s.getsockname()[1])
            s.close()
    return free_ports

print("Free ports:", find_free_ports())
