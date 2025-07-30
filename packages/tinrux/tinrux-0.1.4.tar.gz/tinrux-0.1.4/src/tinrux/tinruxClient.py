# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
# Copyright (c) 2025 Guillermo Leira Temes
# 
import socket

class TinruxClient:
    def __init__(self, hostname, port, buffer_size=1024*1024):
        self.host = hostname
        self.port = port
        self.buffer = buffer_size
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()

    def connect(self):
        try:
            self.socket.connect((self.host, self.port))
            print(f"[+] Connected to Tinrux server at {self.host}:{self.port} [+]")
        except socket.error as e:
            print(f"[!] Error connecting to server: {e} [!]")
            exit()

    def send_command(self, command, *args):
        redis_command = self.format_command(command, *args)
        try:
            self.socket.sendall(redis_command.encode())
            response = self.socket.recv(self.buffer).decode()
            return self.parse_response(response)
        except socket.error as e:
            print(f"[!] Error sending command: {e} [!]")
            return None

    def format_command(self, command, *args):
        parts = ["*" + str(len(args) + 1),
                 "$" + str(len(command)),
                 command.upper()]
        for arg in args:
            arg_str = str(arg)
            parts.append("$" + str(len(arg_str)))
            parts.append(arg_str)
        return "\r\n".join(parts) + "\r\n"

    def parse_response(self, response):
        if response.startswith("+"):
            return response.strip()[1:]
        elif response.startswith("-"):
            return response.strip()[1:]
        elif response.startswith("$"):
            lines = response.strip().split("\r\n")
            if lines[0] == "$-1":
                return None
            elif len(lines) == 2:
                return lines[1]
            else:
                return response.strip()
        elif response.startswith(":"):
            return int(response[1:].strip())
        else:
            return response.strip()

    def close(self):
        self.socket.close()
        print("[*] Connection closed [*]")
