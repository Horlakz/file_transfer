import tkinter as tk
from tkinter import filedialog
import socket
import threading

# Global variable to track the mode (send or receive)
is_sending = True
server_ip = "192.168.0.192"
server_port = 51234
server_running = False

def toggle_mode():
    global is_sending
    is_sending = not is_sending
    if is_sending:
        mode_label.config(text="Mode: Send")
        send_button.config(state=tk.NORMAL)
        start_server_button.config(state=tk.DISABLED)
    else:
        mode_label.config(text="Mode: Receive")
        send_button.config(state=tk.DISABLED)
        start_server_button.config(state=tk.NORMAL)


def get_local_ip():
    try:
        # Create a socket to an external service (Google DNS)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        local_ip = sock.getsockname()[0]
        sock.close()
        return local_ip
    except Exception as e:
        return "Error: " + str(e)

def send_file():

    def send_thread():
        global server_ip
        server_ip = get_local_ip()
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))

        file_path = filedialog.askopenfilename()
        with open(file_path, 'rb') as file:
            data = file.read(1024)
            while data:
                client_socket.send(data)
                data = file.read(1024)

        print(f"File sent successfully: {file_path}")
        client_socket.close()

    # start the server in a separate thread so that it doesn't block the GUI
    send_thread = threading.Thread(target=send_thread)
    send_thread.start()

def start_server():
    global server_running
    global server_ip
    server_ip = get_local_ip()

    def server_thread():
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((server_ip, server_port))
        server_socket.listen(1)

        status_label.config(text=f"Server listening on {server_ip}:{server_port}")

        client_socket, client_address = server_socket.accept()
        status_label.config(text=f"Connection from {client_address}")

        file_name = client_socket.recv(1024).decode()

        with open(file_name, 'wb') as file:
            data = client_socket.recv(1024)
            while data:
                file.write(data)
                data = client_socket.recv(1024)

        status_label.config(text="File received successfully")
        client_socket.close()
        server_socket.close()

    if not server_running:
        server_running = True
        # start the server in a separate thread so that it doesn't block the GUI
        server_thread = threading.Thread(target=server_thread)
        server_thread.start()

def close_server():
    global server_running
    server_running = False
    status_label.config(text="Server stopped")

# Create the main window
root = tk.Tk()
root.title("File Transfer")

# Create a button to toggle between send and receive modes
mode_label = tk.Label(root, text="Mode: Send")
mode_label.pack()
toggle_button = tk.Button(root, text="Toggle Mode", command=toggle_mode)
toggle_button.pack()

# Create a button to select and send a file
send_button = tk.Button(root, text="Select and Send File", command=send_file)
send_button.pack()

# Create a button to start the server
start_server_button = tk.Button(root, text="Start Server", command=start_server, state=tk.DISABLED)
start_server_button.pack()

# Create a button to close the server
close_server_button = tk.Button(root, text="Close Server", command=close_server)
close_server_button.pack()

# Create a label to display status
status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()
