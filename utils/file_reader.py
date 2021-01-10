"""
This class aims to read any kind of file by lazy loading
"""


class FileReader:

    @staticmethod
    def _lazy_reading(file_object, chunk_size):
        """
        Reads the file by chunks in bytes
        :param file_object: a file object
        :param chunk_size:
        """
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data

    def read_file(self, path, chunk_size=1024) -> bin:
        """
        Reads the file by a lazy loading
        :param chunk_size: the max o size which will be read
        :param path: the path for the file
        :return: the string file
        """
        with open(path, "rb") as file:
            full_file = "".encode()
            for piece in self._lazy_reading(file, chunk_size):
                full_file += piece
        return full_file
