from logging import getLogger
from pathlib import Path
try:
    from .err import *
except ImportError:
    from err import *

import requests


class LinkRequester:
    """
    Class to request a link and write the file content to a specified directory.

    Attributes:
        DEFAULT_FILE_OUTPUT_DIR (Path): Default directory for file output.

    Methods:
        __init__(self, url_str: str, api_key: str = None, **kwargs):
            Initialize the LinkRequester object.

        GetWriteFile(cls, **kwargs):
            Class method to create a LinkRequester object and call the _write_file method.

        url_string(self):
            Getter method for the url_string property.

        file_content(self):
            Getter method for the file_content property.

        _initialize_file_output_directory(self):
            Private method to initialize the file output directory.

        _get_file(self, **kwargs):
            Private method to send a GET request to the url and return the content.

        _write_file(self):
            Private method to write the file content to the specified directory.
    """
    DEFAULT_FILE_OUTPUT_DIR = Path('../Misc_Project_Files/Signatures')

    def __init__(self, url_str: str, api_key: str = None, **kwargs):
        self.logger = kwargs.get('logger', getLogger(self.__class__.__name__))
        self.logger.info(f'Starting initialization of {self.__class__.__name__}')
        self.__api_key = api_key
        self._url_string = url_str
        self._file_content = None

        self._initialize_file_output_directory()

        self.full_file_output_path = self.DEFAULT_FILE_OUTPUT_DIR.joinpath(kwargs.get('filename',
                                                                                      self.url_string.split('/')[-1]))
        self.logger.debug(f'file output set to {self.full_file_output_path}')
        self.logger.info(f'{self.__class__.__name__} initialized')

    @classmethod
    def GetWriteFile(cls, **kwargs):
        """
        This method is a class method that allows for the creation of a new instance of the class and immediately calls
        the private method `_write_file()`. It returns the result of the `_write_file()` method.

        Parameters:
            **kwargs: The keyword arguments used for creating an instance of the class.

        Returns:
            The result of calling the `_write_file()` method.
        """
        return cls(**kwargs)._write_file()

    @property
    def url_string(self):
        """
        This is a property method called `url_string` in a class. It is used to validate and retrieve the url string.

        Raises:
            - SignatureFileError: If the url string is invalid, an exception of type SignatureFileError is raised.

        Returns:
            - str: The valid url string if it meets the specified conditions.

        Note:
            - The url_string should start with 'http', contain 'www.jotform.com/' in the middle, and end with '.png'.
            - If the url_string does not meet these conditions, a SignatureFileError is raised and logged.

        Example usage:
            - obj = ClassName()
            - obj.url_string = 'https://www.jotform.com/abc.png'  # Valid url string
            - url_str = obj.url_string  # Retrieves the valid url string
        """
        if (self._url_string.startswith('http')
                and self._url_string.split('www.')[-1].startswith('jotform.com/')
                and self._url_string.endswith('png')):
            return self._url_string
        try:
            raise SignatureFileError(f'invalid link string: {self._url_string}')
        except SignatureFileError as e:
            self.logger.error(e, exc_info=True)
            raise e

    @property
    def file_content(self):
        """
        @property
        def file_content(self):
            Gets the content of a file.

            If the file content has not been retrieved yet, it retrieves the content by calling the _get_file() method.
            If an HTTP error occurs during the retrieval, a SignatureFileError is raised, and the error is logged using the logger.
            After retrieving the file content, it is stored in the _file_content attribute.

            Returns:
                The content of the file.
        """
        if not self._file_content:
            self._file_content = self._get_file()
            if isinstance(self._file_content, requests.HTTPError):
                try:
                    raise SignatureFileError(self._file_content)
                except SignatureFileError as e:
                    self.logger.error(e, exc_info=True)
                    raise e
        self.logger.debug('returning file_content.')
        return self._file_content

    def _initialize_file_output_directory(self):
        """
        This method is responsible for initializing the file output directory.
        If the default file output directory already exists, it logs a debug message and does nothing.
        If the output directory does not exist, it tries to create it and logs a debug message if successful.
        If there is an error during directory creation, it logs an error message and raises a SignatureFileError.

        Parameters:
        None

        Returns:
        None

        Raises:
        SignatureFileError: If there is an error during directory creation

        Example usage:
        obj = YourClass()
        obj._initialize_file_output_directory()
        """
        if self.DEFAULT_FILE_OUTPUT_DIR.is_dir():
            self.logger.debug(f'{self.DEFAULT_FILE_OUTPUT_DIR} detected')
        else:
            try:
                self.DEFAULT_FILE_OUTPUT_DIR.mkdir()
                self.logger.debug(f'{self.DEFAULT_FILE_OUTPUT_DIR} created')
            except (IsADirectoryError, FileNotFoundError) as e:
                self.logger.error(f'unable to create directory: {self.DEFAULT_FILE_OUTPUT_DIR}')
                raise SignatureFileError(e) from e

    def _get_file(self, **kwargs):
        """
        This method is used to send a GET request to a specified URL and retrieve the content of the response.

        Parameters:
        - **kwargs: Any additional keyword arguments can be passed to the method.
        The 'api_key' keyword argument will be used to provide the API key.

        Returns:
        - bytes: The content of the response if the request was successful.

        Raises:
        - SignatureFileError: If the request encountered an error.

        Example:
        get_file(api_key='your_api_key')
        """
        self.logger.info(f'Attempting GET request to url {self.url_string}')
        r = requests.get(self.url_string, params={'apiKey': kwargs.get('api_key', self.__api_key)})
        if r.ok:
            self.logger.info(f'request OK (code: {r.status_code}), returning content.')
            return r.content
        # implied else here
        raise SignatureFileError(r.raise_for_status())

    def _write_file(self):
        """
        Writes the file content to the specified output path.

        The `_write_file` function writes the contents of the file to the specified output path.
        It opens the file in binary mode and writes the file content using the `write` method of the file object.

        Parameters:
            self (object): The current object instance.

        Returns:
            None

        Raises:
            None
        """
        with open(self.full_file_output_path, 'wb') as f:
            f.write(self.file_content)
