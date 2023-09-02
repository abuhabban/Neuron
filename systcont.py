import os
import speech_recognition as sr
from flask import Flask, request, jsonify
import threading
import socket

app = Flask(__name__)

class SystemController:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "0.0.0.0"  # Listen on all available network interfaces.
        self.port = 12345  # Change this to any available port you prefer.

    def _check_and_install_module(self, module_name):
        try:
            __import__(module_name)
            return True
        except ImportError:
            print(f"{module_name} is not installed. Installing...")
            os.system(f"pip install {module_name}")
            return True

    def check_dependencies(self):
        # Check and install required modules.
        dependencies = ["speech_recognition"]
        for dependency in dependencies:
            self._check_and_install_module(dependency)

    def _perform_action(self, action, time=0):
        """
        Performs a system action (shutdown, restart, or logout) without user input.

        Args:
            action (str): The action to perform ("shutdown", "restart", or "logout").
            time (int, optional): The delay in seconds before performing the action (default is 0).

        Returns:
            str: A message indicating the result of the action.
        """
        if action not in ["shutdown", "restart", "logout"]:
            return "Invalid action. Use 'shutdown', 'restart', or 'logout'."

        if action == "logout":
            result = os.system(f"shutdown -l /t {time}")
        else:
            result = os.system(f"shutdown /{action[0]} /t {time}")

        if result == 0:
            return f"{action.capitalize()} initiated with a {time}-second delay..."
        else:
            return f"Failed to {action}."

    def _handle_voice_command(self):
        with sr.Microphone() as source:
            print("Listening for voice command...")
            audio = self.recognizer.listen(source)

        try:
            command = self.recognizer.recognize_google(audio).lower()
            print(f"Voice command recognized: {command}")
            if "shutdown" in command:
                self._perform_action("shutdown")
            elif "restart" in command:
                self._perform_action("restart")
            elif "logout" in command:
                self._perform_action("logout")
            elif "manual" in command:
                self._handle_manual_input()
            else:
                print("Unrecognized command. Please use 'shutdown', 'restart', 'logout', or 'manual'.")

        except sr.UnknownValueError:
            print("Could not understand the audio.")
        except sr.RequestError as e:
            print(f"Error with the speech recognition service: {e}")

    def _handle_manual_input(self):
        while True:
            print("Manual Input Command Mode:")
            print("1. Shutdown")
            print("2. Restart")
            print("3. Logout")
            print("4. Exit")

            choice = input("Enter your choice (1/2/3/4): ")

            if choice == "1":
                self._perform_action("shutdown")
            elif choice == "2":
                self._perform_action("restart")
            elif choice == "3":
                self._perform_action("logout")
            elif choice == "4":
                break
            else:
                print("Invalid choice. Please enter a valid option (1/2/3/4).")

    def start(self):
        self.check_dependencies()

        while True:
            print("Select Mode:")
            print("1. Voice Command Mode")
            print("2. Manual Input Command Mode")
            print("3. Start Server")
            print("4. Exit")

            mode_choice = input("Enter your choice (1/2/3/4): ")

            if mode_choice == "1":
                self._handle_voice_command()
            elif mode_choice == "2":
                self._handle_manual_input()
            elif mode_choice == "3":
                self.start_server()
            elif mode_choice == "4":
                break
            else:
                print("Invalid choice. Please enter a valid option (1/2/3/4).")

    def start_server(self):
        self.server.bind((self.host, self.port))
        self.server.listen(1)  # Listen for one incoming connection.

        print(f"Server is listening on {self.host}:{self.port}...")

        while True:
            client_socket, _ = self.server.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.start()

    def handle_client(self, client_socket):
        while True:
            command = client_socket.recv(1024).decode()
            if not command:
                break

            if command == "shutdown" or command == "restart" or command == "logout":
                self._perform_action(command)
            else:
                client_socket.send("Invalid command.".encode())

# Create an instance of the SystemController
controller = SystemController()

@app.route('/perform_action', methods=['POST'])
def perform_action():
    data = request.get_json()
    action = data.get('action')
    time = data.get('time', 0)  # Default time is 0 seconds

    if action in ["shutdown", "restart", "logout"]:
        result = controller._perform_action(action, time)
        return jsonify({'message': result})
    else:
        return jsonify({'error': 'Invalid action'})

if __name__ == "__main__":
    controller.check_dependencies()
    
    # Start the Flask web server in a separate thread
    server_thread = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000})
    server_thread.start()
    
    # Start the main program
    controller.start()
