"""
Write a function which detects if entered string is http/https domain name with optional slash at the and
Restriction: use re module
Note that address may have several domain levels
    >>>is_http_domain('http://wikipedia.org')
    True
    >>>is_http_domain('https://ru.wikipedia.org/')
    True
    >>>is_http_domain('griddynamics.com')
    False
"""
import re
import pytest


def is_http_domain(domain: str) -> bool:
    r = re.match(r'^https?://\w+\.\w+(\.\w+)*/?', domain)
    if not r:
        return False
    if r.span() != (0, len(domain)):
        return False
    return True


"""
write tests for is_http_domain function
"""


class TestIsHttpDomain:
    TEST_DOMAINS = [
        ('http://wikipedia.org', True),
        ('http://wikipedia.org/', True),
        ('https://ru.wikipedia.org', True),
        ('https://ru.wikipedia.org/', True),
        ('https://ru.wikipedia.org/', True),
        ('/tmp/', False),
        ('http:/tmp/', False),
        ('http://tmp', False),
        ('http://tmp.org.', False),
        ('http://tmp.org./', False),
        ('http://tmp.org..ru/', False),
        ('http://.google.com', False),
    ]

    @pytest.mark.parametrize('test_input,expected', TEST_DOMAINS)
    def test_domains(self, test_input, expected):
        assert is_http_domain(test_input) == expected
