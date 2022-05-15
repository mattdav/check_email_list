from dns import resolver
from pathlib import WindowsPath
import pandas as pd
from pandas import DataFrame
from requests import Response
import unidecode
import random
import requests
import logging
log = logging.getLogger(__name__)


def split_email(email: str) -> list:
    """Split email into prefix and domain name

    :param email: Input email
    :type email: str
    :return: List of prefix and domain name
    :rtype: list
    """
    temp = email.rsplit('@', 1)
    email_parts = {'full_email': email, 'prefix': temp[0], 'domain': temp[1]}
    return email_parts


def dns_check(domain: str) -> bool:
    """Check if domain name exist

    :param domain: Domain to check
    :type domain: str
    :return: True if domain exist, false otherwise
    :rtype: bool
    """
    try:
        resolver.resolve(domain, 'MX')
        return True
    except resolver.NoAnswer:
        return False


def read_file(file_path: WindowsPath) -> list:
    """Read text file from path, used to load domains lists

    :param file_path: Path to the file
    :type file_path: WindowsPath
    :raises e: Raise a FileNotFoundError if the file doesn't exist
    :return: Return the list of domains in text files
    :rtype: list
    """
    try:
        with open(file_path) as f:
            content = f.readlines()
    except FileNotFoundError as e:
        logging.error(
            f"The file {file_path} doesn't exist.",
            exc_info=True,
        )
        raise e
    domains = [domain.strip() for domain in content]
    return domains


def read_csv(csv_path: WindowsPath) -> DataFrame:
    """Read csv file, used to load email list

    :param csv_path: Path to CSV
    :type csv_path: WindowsPath
    :return: Dataframe loaded
    :rtype: DataFrame
    """
    df = pd.read_csv(csv_path, sep=';', encoding='latin-1')
    return df


def write_list_to_text(list: list, text_path: WindowsPath):
    """Write list to text file

    :param list: List to write
    :type list: list
    :param text_path: Path to text file
    :type text_path: WindowsPath
    """
    with open(text_path, 'w') as f:
        for domain in list:
            f.write(domain)
            f.write('\n')


def prep_text(text: str) -> str:
    """Lower and strip accent from string

    :param text: String to process
    :type text: str
    :return: Resulting string
    :rtype: str
    """
    text = unidecode.unidecode(text)
    text = text.lower().strip()
    return text


def requests_email(email: str, 
                   user_agents: list) -> tuple[int, str]:
    """Post requests to check email from external website

    :param email: Email to check
    :type email: str
    :param user_agents: List of user-agents to avoid robot.txt detection
    :type user_agents: list
    :return: Return status code and text from response
    :rtype: Response
    """
    url = "https://www.verifyemailaddress.org/"
    ua = user_agents[random.randrange(len(user_agents))]
    headers = {'user-agent': ua, 'referer': 'https://www.verifyemailaddress.org/'}
    data = {'email': email}
    r = requests.post(url, headers=headers, data=data)
    status = r.status_code
    text = r.text
    r.close()
    return status, text
