import socket


def get_host_ip() -> str:
    host_ip: str = "0.0.0.0"
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        host_ip: str = str(s.getsockname()[0])
    finally:
        s.close()
        return host_ip