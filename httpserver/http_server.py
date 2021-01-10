"""
This class represents a simple web sever using TCP Sockets
"""
import datetime
import mimetypes
import os
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
from utils.file_reader import FileReader

BUFFER_SIZE = 2048

STATUS_RESPONSE = {
    200: "Ok",
    404: "Not Found",
    400: "Bad Request",
    505: "Version Not supported"
}

STATUS_MESSAGE = {
    404: "The requested URL was not found on this server.",
    400: "Your client sent a request that this server could not understand.",
    505: "Your client sent a request with a version not supported for this server"
}

ROOT = "../utils/banana"


class HttpServer:
    """
    This class represents a Implementation of a Http 1.1 webServer
    """

    def __init__(self, address: str, port: int):
        self.__server_socket = socket(AF_INET, SOCK_STREAM)
        self.__server_port = port
        self.__server_address = address
        self.__server_socket.bind((address, port))
        self.__file_reader = FileReader()

    def start_server(self):
        """
        Stars the sever and listen for tcp requests
        """
        self.__server_socket.listen()
        print(f"listening on port: {self.__server_port}")
        while True:
            (client_socket, client_address) = self.__server_socket.accept()
            Thread(target=self._get_data, args=(client_socket,)).start()

    @staticmethod
    def _is_protocol_right(message: str) -> bool:
        """
        Checks if the message is in the correct pattern
        :return: the flag
        """
        flag = True
        method: str = message[:3]
        if method != "GET":
            flag = False
        return flag

    @staticmethod
    def _is_version_correct(message: str) -> bool:
        """
        Checks if the HTTP version is 1.1 or 1.1
        :param message: the http protocol pattern
        :return: true or false
        """
        line: str = message.splitlines()[0]
        version: str = line.split("/")[-1]
        return version in ('1.0', '1.1')

    @staticmethod
    def is_file_in_the_server(path: str) -> bool:
        """
        Verifies if the path matches with a file on the server
        :param path: the path for file
        :return: a flag which can be true or false
        """
        flag = False
        elements = path.split("/")[1:]
        current_location = ROOT
        for element in elements:
            files_list = os.listdir(current_location)
            if element in files_list:
                flag = True
                current_location += "/" + element
            else:
                flag = False
                break
        return flag

    def _get_data(self, client_socket):
        """
        Gets the client message and verifies the protocol
        :param client_socket: The client Socket
        """
        print("Connection accepted")
        data = client_socket.recv(BUFFER_SIZE)
        msg: str = data.decode()
        path = self._get_path(msg)
        status_code = self._get_status_code(msg)
        self._send_data(client_socket, status_code, path)

    @staticmethod
    def _get_path(protocol: str) -> str:
        """
        Gets the file path in the protocol
        :param protocol: the http protocol
        :return: the file path
        """
        line: str = protocol.splitlines()[0]
        path = line.split(" ")[1]
        return path

    def _get_status_code(self, message_protocol: str) -> str:
        """
        Gets the status code due the http patterns
        :param (string) message_protocol: the http 1.1 pattern
        :return:(string) the status code
        """
        if self._is_protocol_right(message_protocol):
            if self._is_version_correct(message_protocol):
                if (self._get_path(message_protocol)) == "/":
                    status_code = "200"
                else:
                    if self.is_file_in_the_server(self._get_path(message_protocol)):
                        status_code = "200"
                    else:
                        status_code = "404"
            else:
                status_code = "505"
        else:
            status_code = "400"
        return status_code

    @staticmethod
    def _remove_root(path: str) -> str:
        """
        Removes the ROOT from the path
        :param path: the path
        :return: the path without the root
        """
        root_length = len(ROOT)
        return path[root_length:]

    @staticmethod
    def is_directory_created() -> bool:
        """
        Checks if the Root is a real directory in the OS
        :return:
        """
        return os.path.isdir(ROOT)

    @staticmethod
    def _get_mime_type(file: str) -> str:
        """
        Gets the mime_type of a file
        :param file: a file
        :return: the mimetype
        """
        return mimetypes.MimeTypes().guess_type(file)[0]

    @staticmethod
    def _format_response(status_code: str, mime_type) -> str:
        """
        Formats the response due to the status code
        :param status_code: http pattern for status code
        :return: the formatted response
        """
        time = datetime.datetime.now()
        year = str(time.year)
        day = time.strftime("%a")
        day_of_month = time.strftime("%d")
        month = time.strftime("%b")
        current_hour = time.strftime("%X")

        protocol = (f'HTTP/1.1 {status_code} {STATUS_RESPONSE[int(status_code)]}\r\n'
                    f'Date: {day}, {day_of_month} {month} {year} {current_hour} GMT\r\n'
                    f'Server: ZS/0.0.1 (Ubuntu)\r\n'
                    f'Content-Type: {mime_type}\r\n'
                    '\r\n')
        return protocol

    @staticmethod
    def _get_modification_date(file_path: str) -> str:
        """
        Gets the last modification date given an file path
        :param file_path: the file path
        :return: the last modification of the given file
        """
        last_use = os.path.getmtime(file_path)
        return str(datetime.datetime.fromtimestamp(last_use)).split(".")[0]

    def _create_index(self, directory=ROOT) -> bin:
        """
        Creates the directory explorer
        :param: directory: an directory
        :return: A template for a directory explorer
        """
        files = os.listdir(directory)
        colspan = str(len(files) + 1)
        relative_path = self._remove_root(directory)
        current_path = "/"
        if directory != ROOT:
            current_path = relative_path
        if len(files) == 0:
            colspan = 0
        html_main = (
            '<html lang="pt-BR">'
            '<head>'
            f'<title> Index of {current_path} </title>'
            '</head>'
            '<body>'
            f'<h1> Index of {current_path} </h1>'
            '<table>'
            '<tr>'
            f'<th valign="top"><img src="../utils/files/ico.png" alt="[ICO]"></th>'
            '<th><a> Name </a> </th>'
            '<th><a> Last modified </a></th>'
            '<th><a> Size </a></th>'
            '<th><a> Description </a></th></tr>'
            '<tr>'
            f'<th colspan={colspan}><hr></th></tr>'
        )
        file_extension = "[FILE]"
        for file in files:
            if directory != ROOT:
                file = relative_path + "/" + file
            extension = file_extension if len(file.split(".")) > 1 else "[DIR]"
            full_file_path = ROOT + "/" + file
            line = (
                '<tr>'
                f'<td valign="top"><img src="../utils/files/ico.png" alt={extension}></td>'
                f'<td><a href={file}>{file}</a></td>'
                f'<td align="right">{self._get_modification_date(full_file_path)}</td>'
                f'<td align="right">{os.path.getsize(full_file_path)/1024} Kb</td>'
                f'<td>&nbsp;</td>'
                '</tr>'
            )
            html_main += line
        bottom_html = (
            f'<tr><th colspan={colspan}><hr></th></tr>'
            '</table>'
            f'<address>ZS server (Ubuntu) '
            f'Server at {self.__server_address} Port {self.__server_port}</address>'
            '</body></html>'
        )
        html_main += bottom_html
        return html_main.encode()

    def _create_error_template(self, status_code: str) -> bin:
        """
        Builds a template for each error status code
        :param status_code: the http status code
        :return: the template in binary
        """
        template = (
            '<html><head>'
            f'<title>{status_code} {STATUS_RESPONSE[int(status_code)]}</title></head><body>'
            f'<h1>{STATUS_RESPONSE[int(status_code)]}</h1>'
            f'<p>{STATUS_MESSAGE[int(status_code)]}</p><hr>'
            f'<address> ZS / 1.0.0(Ubuntu) Server at '
            f'{self.__server_address} Port {self.__server_port}</address>'
            '</body></html>'
        ).encode()
        return template

    def _send_data(self, client_socket, status_code: str, path: str):
        """
        Sends a message to the client
        :param client_socket: The client socket
        :param status_code: A Http status code
        """
        mime_type = "text/html"

        if status_code == "200":
            if path == '/':
                if not self.is_directory_created():
                    os.mkdir(ROOT)
                content = self._create_index()
            else:
                full_path = ROOT + path
                if len(path.split('.')) > 1:
                    file: bin = self.__file_reader.read_file(full_path)
                    content = file
                    file_name = full_path.split("/")[-1]
                    mime_type = self._get_mime_type(file_name)
                else:
                    content = self._create_index(full_path)
        else:
            content = self._create_error_template(status_code)

        protocol = HttpServer._format_response(status_code, mime_type)
        final_message = protocol.encode()
        data = final_message + content
        client_socket.send(data)
        client_socket.close()


if __name__ == "__main__":
    httpSv = HttpServer('localhost', 8001)
    httpSv.start_server()
