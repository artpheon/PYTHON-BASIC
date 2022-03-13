"""
Write a function that makes a request to some url
using urllib. Return status code and decoded response data in utf-8
Examples:
     >>> make_request('https://www.google.com')
     200, 'response data'
"""
from unittest import TestCase
from unittest.mock import patch, MagicMock
from typing import Tuple
from urllib import request


def make_request(url: str) -> Tuple[int, str]:
    with request.urlopen(url) as r:
        return r.status, r.read().decode('utf-8')
    # r = None
    # try:
    #     r = request.urlopen(url)
    # except Exception as exc:
    #     print(exc)
    # else:
    #     return r.status, r.read().decode('utf-8')
    # finally:
    #     if r:
    #         r.close()


"""
Write test for make_request function
Use Mock for mocking request with urlopen https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock
Example:
    >>> m = Mock()
    >>> m.method.return_value = 200
    >>> m.method2.return_value = b'some text'
    >>> m.method()
    200
    >>> m.method2()
    b'some text'
"""


class TestMakeRequest(TestCase):
    STATUS = 200
    BYTE_RESP = b'some random bytes: \xd0\xb2\xd0\xba'
    STR_RESP = 'some random bytes: вк'
    DUMMY_URL = 'http://google.com'

    @patch('urllib.request.urlopen')
    def test_make_request(self, mock_open):
        m = MagicMock()
        mock_response = m.http.client.HTTPResponse()
        mock_response.__enter__().status = self.STATUS
        mock_response.__enter__().read.return_value = self.BYTE_RESP
        mock_open.return_value = mock_response
        result = make_request(self.DUMMY_URL)
        assert mock_open.called_once()
        assert result[0] == self.STATUS
        assert result[1] == self.STR_RESP
