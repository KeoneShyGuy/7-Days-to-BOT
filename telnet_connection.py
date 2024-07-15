import telnetlib
import time

class TelnetConnection:
    def __init__(self):
        self.telnet = None
        self.host = ""
        self.port = 0
        self.password = ""
        self.server_info = {}

    def load_config(self):
        with open('config.txt', 'r') as f:
            for line in f:
                try:
                    name, value = line.strip().split('=', 1)
                    if name == 'TELNET_HOST':
                        self.host = value
                    elif name == 'TELNET_PORT':
                        self.port = int(value)
                    elif name == 'TELNET_PASSWORD':
                        self.password = value
                except ValueError:
                    print(f"Skipping malformed config line: {line.strip()}")

    def load_server_info(self):
        with open('server_info.txt', 'r') as f:
            for line in f:
                try:
                    name, value = line.strip().split('=', 1)
                    self.server_info[name] = value
                except ValueError:
                    print(f"Skipping malformed server info line: {line.strip()}")

    def connect(self):
        self.load_config()
        try:
            print("Connecting to Telnet server...")
            self.telnet = telnetlib.Telnet(self.host, self.port)
            
            def wait_for_keyword(keyword, timeout=10):
                end_time = time.time() + timeout
                while time.time() < end_time:
                    response = self.telnet.read_very_eager().decode('ascii', errors='ignore')
                    if keyword in response:
                        print(f"Found keyword: {keyword}")
                        return True
                    time.sleep(0.5)
                return False
            
            attempts = 0

            while True:
                print("Waiting for password prompt...")
                if wait_for_keyword("password"):
                    attempts += 1
                    print(f"Sending password (Attempt {attempts})...")
                    self.telnet.write(self.password.encode('ascii') + b"\n")
                
                    print(f"Waiting for possible second password prompt (Attempt {attempts})...")
                    if wait_for_keyword("password", timeout=5):
                        attempts += 1
                        print(f"Sending password again (Attempt {attempts})...")
                        self.telnet.write(self.password.encode('ascii') + b"\n")
                
                    time.sleep(2)
                    print("Successfully connected to the Telnet server.")
                    break
                else:
                    print("Password prompt not found.")
                    self.telnet.close()
                    break
        except Exception as e:
            print(f'Error: {e}')

    def send_command(self, command):
        try:
            self.telnet.write(command.encode('ascii') + b"\n")
            time.sleep(2)
            response = self.telnet.read_very_eager().decode('ascii', errors='ignore')
            return response.strip()
        except Exception as e:
            print(f'Error sending command: {e}')
            return None

# Example usage
if __name__ == "__main__":
    connection = TelnetConnection()
    connection.connect()
    response = connection.send_command("gettime")
    print("Server response:", response)
