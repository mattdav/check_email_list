import re
import requests
import random
import pandas as pd
from bs4 import BeautifulSoup
from bin.utils import dns_check, requests_email


def check_domains(domains: list) -> list:
    """Check list of domains to keep only valid ones

    :param domains: List of known domains loaded from text file
    :type domains: list
    :return: List of valid domains that have been verified with dns check
    :rtype: list
    """
    valid_domains = [domain for domain in domains if dns_check(domain)]
    return valid_domains


def is_empty(email: str) -> bool:
    """Check that the email is not empty

    :param email: Input email
    :type email: str
    :return: True if the email is empty, false otherwise
    :rtype: bool
    """
    if pd.isna(email):
        return True
    else:
        return False


def is_syntax_correct(email: str) -> bool:
    """Check if the email format is a valid one

    :param email: Input email to check
    :type email: str
    :return: True if the email is valid, false otherwise
    :rtype: bool
    """
    regex = r'([A-Za-z0-9]+[.-_!#$%&\?\+\'\*\/\=\^])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,3})+'
    if re.fullmatch(regex, email):
        return True
    else:
        return False


def is_domain_valid(domain: str,
                    valid_domains: list,
                    disposable_domains: list) -> tuple[int, list]:
    """Check if domain of email address ex.istitle()
    First by checking in the valid list
    Then by sending a dns request to check it directly
    If the dns request respond positively, the domain is added
    to the valid list for the next checks

    :param email: Domain of input email
    :type email: str
    :param valid_domains: List of domains that have already been approved
    :type valid_domains: list
    :param disposable_domains: List of domains that are known to provide
    disposable addresses
    :type disposable_domains: list
    :return: First parameter is the response:
        0 for existing domain
        3 for spam domain
        4 for non-existing domain
    Second parameter is the valid domains list eventually completed
    :rtype: tuple[int, list]
    """
    if domain in valid_domains:
        return 0, valid_domains
    elif domain in disposable_domains:
        return 3, valid_domains
    elif dns_check(domain):
        valid_domains.append(domain)
        return 0, valid_domains
    else:
        return 4, valid_domains


def email_exist(email: str, user_agents: list) -> int:
    """Check if email exist based on online email checker

    :param email: Input email
    :type email: str
    :param user_agents: List of user agent to pass to requests
    :type user_agents: list
    :return: Status of answer
    0 : email does exist
    2 : email syntax is incorrect
    5 : domain server does not provide answer
    6 : email does not exist
    :rtype: int
    """
    status, text = requests_email(email, user_agents)
    if status == 200:
        html = BeautifulSoup(text, 'html.parser')
        results = html.find_all(id='result')[0].find('ul').find_all('li')
        status = [result.attrs['class'][0] for result in results]
        if len(status) == 1:
            return 2
        elif len(status) == 2:
            return 5
        elif (len(status) == 3) and (status[2] == 'failure'):
            return 6
        else:
            return 0
    else:
        return 5
