from fuzzywuzzy import process
from bin.utils import prep_text


def correct_domain(domain: str, domains_list: list) -> str:
    """Suggest correction in case of invalid domain by fuzzymatching
    of false domain with verified domains list

    :param domain: False domain
    :type domain: str
    :param domains_list: List of verified domains
    :type domains_list: list
    :return: Corrected domain if a match have been found
    :rtype: str
    """
    first_letter = domain[0]
    possible_domains = [domain for domain in domains_list if domain[0] == first_letter]
    best_match = process.extractOne(domain, possible_domains)
    if best_match[1] > 50:
        return best_match[0]
    else:
        return ""


def correct_prefix(nom: str, prenom: str, prefix: str) -> str:
    """Suggest corrected prefix from name and surname combinaisons
    in case of typing error

    :param nom: Name of person
    :type nom: str
    :param prenom: Surname of person
    :type prenom: str
    :param prefix: Prefix of email address
    :type prefix: str
    :return: Best combinaison
    :rtype: str
    """
    nom = prep_text(nom)
    prenom = prep_text(prenom)
    list = [f"{nom}.{prenom}", f"{nom}_{prenom}", f"{nom}-{prenom}",
            f"{nom}{prenom}", f"{prenom}.{nom}.", f"{prenom}_{nom}",
            f"{prenom}-{nom}", f"{prenom}{nom}"]
    best_match = process.extractOne(prefix, list)
    if best_match[1] > 50:
        return best_match[0]
    else:
        return ""
