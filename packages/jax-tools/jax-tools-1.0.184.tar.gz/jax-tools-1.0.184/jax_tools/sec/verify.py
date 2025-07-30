"""
Verify the data is safe or not
"""
import re


class Verify(object):
    """
    Verify the data is safe or not
    """

    @classmethod
    def ip_or_domain(cls, s: str) -> bool:
        """
        Verify the argument is a valid ip address or domain name or not
        Args:
            s (str): ip

        Returns:
            bool: True or False
        """
        if cls.ip(s) or cls.domain(s):
            return True
        return False

    @staticmethod
    def ip(ip: str) -> bool:
        """
        Verify the argument is a valid ip address or not
        Args:
            ip (str): ip

        Returns:
            bool: True or False
        """
        match = re.match(r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$', ip)
        if match and len(match.groups()) == 4:
            # print(match.groups())
            return all(0 <= int(group) <= 255 for group in match.groups())
        else:
            # print(f'{ip}这不是一个IP')
            return False

    @staticmethod
    def domain(domain: str) -> bool:
        """
        Verify the argument is a valid domain name or not
        Args:
            domain (str): domain

        Returns:
            bool: True or False
        """

        if re.match(r'^([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\.)+[a-zA-Z]{2,}$', domain):
            return True
        else:
            return False

    @staticmethod
    def url(url: str) -> bool:
        """
        Verify the url is valid url or not
        Args:
            url (str): url

        Returns:

        """
        if re.match(r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2})|[/\w \.-]*)(:\d+)?(\?[=&\w]*)*$',
                    url) and url != 'http://' and url != 'https://':
            return True
        else:
            return False

    @staticmethod
    def nginx_conf(nginx_conf_content: str, while_list: list[str] = ()) -> bool:
        """
        Verify nginx config file is safe or not
        Args:
            nginx_conf_content (str): nginx config file content
            while_list: list[str]: safe content list

        Returns:

        """
        nginx_conf_content = nginx_conf_content.lower()
        risk_str_list = [
            'risk',
            'root',
            'location',
            'alias',
            'rewrite',
            'if',
            'autoindex',
            'return',
            'proxy_pass',

        ]
        # remove safe content
        for s in while_list:
            nginx_conf_content = nginx_conf_content.replace(s.lower(), '')
        # verify risk content exist conf content or not
        for risk_str in risk_str_list:
            if risk_str.lower() in nginx_conf_content:
                return False
        return True

    @staticmethod
    def safe_str(string: str, safe_str_list: tuple[str, ...] = ()) -> bool:
        """
        Verify the string is safe or not
        Args:
            string (str): string
            safe_str_list (tuple): safe string list

        Returns:
            bool: True or False
        """
        for safe_str in safe_str_list:
            string = string.replace(safe_str, '')
        if re.match(r'^[a-zA-Z0-9_]+$', string):
            return True
        else:
            return False


if __name__ == '__main__':
    v = Verify()
    print(v.safe_str('a'))
    print(v.safe_str('a1'))
    print(v.safe_str('a_1'))
    print(v.safe_str('a_1!'))
    print(v.safe_str('a!a'))
    print(v.safe_str('a!a', ('!',)))
