"""Main module used to gather all informations and launch the submodules"""
import logging
import importlib.resources
from pathlib import WindowsPath
from bin.pipeline import process_emails
from bin.utils import read_file, read_csv, write_list_to_text
from bin.checks import check_domains
import os


def get_folder_path(folder_name: str) -> WindowsPath:
    """Get directory path of the package from its name

    Args:
        folder_name (str): Name of the directory

    Raises:
        e: If the directory doesn't exist, raise a NameError

    Returns:
        WindowsPath: Path to the directory
    """
    try:
        with importlib.resources.path(folder_name, "") as p:
            folder_path = p
    except NameError as e:
        logger.error(f"Le dossier {folder_name} n'existe pas.", exc_info=True)
        raise e
    return folder_path


if __name__ == '__main__':
    #: Path to the config directory
    config_path = get_folder_path('config')
    #: Path to the data directory
    data_path = get_folder_path('data')
    #: Path to the log directory
    log_path = get_folder_path('log')
    logger = logging
    logger.basicConfig(filename=os.path.join(log_path, "app.log"),
                       format="%(asctime)s - %(levelname)s - %(message)s",
                       level=logging.DEBUG)
    known_domains = read_file(os.path.join(data_path,
                                           "input/known_domains.txt"))
    # valid_domains = check_domains(known_domains)
    valid_domains = known_domains
    disp_domains = read_file(os.path.join(data_path, "input",
                                                "disposable_domains.txt"))
    user_agents = read_file(os.path.join(data_path, "input/user_agents.txt"))
    df_email = read_csv(os.path.join(data_path, 'input/email.csv'))
    df_email_checked = process_emails(df_email, valid_domains, disp_domains,
                                      user_agents)
    df_email.to_csv(os.path.join(data_path, 'output/email_checked.csv'),
                    sep=';',
                    encoding='latin-1')
    os.remove(os.path.join(data_path, "input/known_domains.txt"))
    write_list_to_text(valid_domains,
                       os.path.join(data_path, "input/known_domains.txt"))
