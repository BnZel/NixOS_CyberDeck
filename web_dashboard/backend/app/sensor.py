import paramiko, ast, threading, time
from paramiko import SSHClient 

class Sensor:
    def __init__(self):
        self.all_output = ""
        self.gps_output = "" 
        self.baro_output = "" 
        self.cpu_output = ""

        self.thread = None
        self.thread_running = False
        self.start_thread()

    def start_thread(self):
        '''
        multithreaded process to run
        startup script on NixOS cyberdeck
        to prevent blocking due to the script
        indefinitely running
        '''
        if self.thread is None or not self.thread.is_alive():
            print("Starting Thread...")
            self.thread = threading.Thread(target=self.connect, daemon=True)
            self.thread.start()
        
    def connect(self):
        '''
        SSH connection and continue
        monitoring output from script
        and idenitfy hardware to output
        to an appropriate endpoint
        '''
        try:
            print("Establishing Connection.....")
            client = SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect('10.0.0.245',username='jay',password='1875')
            
            transport = client.get_transport()
            channel = transport.open_session()
            transport.set_keepalive(60)

            stdin, stdout, stderr = client.exec_command('source ~/.zshrc; nix-shell default.nix --run "sh run_py.sh TEST"', get_pty=True)

            while True:
                if stdout.channel.recv_ready():
                    self.all_output = stdout.channel.recv(2048).decode("utf-8")
                    self.type_check()

        except KeyboardInterrupt as e:
            print(f"Keyboard Interrupt Exit: {e}")
            client.exec_command('pkill -2 -f test.py')
            client.close()
            channel.close()

        except paramiko.AuthenticationException as e:
            print(f"Authentication Error: {e}")

        except paramiko.SSHException as e:
            print(f"SSH Error: {e}")

        finally:
            print("Closing connection")
            channel.close()
            client.close()

    def type_check(self):
            '''
            check which type of hardware
            is being outputted and return it
            '''
            if str(self.all_output).startswith("gps"): 
                self.all_output = ast.literal_eval(self.all_output.lstrip("gps"))
                self.gps_output = self.all_output
                return self.gps_output
            
            elif str(self.all_output).startswith("barometric"):
                self.all_output = ast.literal_eval(self.all_output.lstrip("barometric"))
                self.baro_output = self.all_output
                return self.baro_output
            
            elif str(self.all_output).startswith("cpu"):
                self.all_output = ast.literal_eval(self.all_output.lstrip("cpu"))
                self.cpu_output = self.all_output
                return self.cpu_output 
            
            else:
                return "No data or existing devices..."
