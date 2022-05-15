from pandas import DataFrame
from bin.checks import is_empty, is_syntax_correct, is_domain_valid, email_exist
from bin.utils import split_email
from bin.correct import correct_domain, correct_prefix


def pipeline_email(infos: DataFrame,
                   valid_domains: list,
                   disposable_domains: list,
                   user_agents: list) -> tuple[int, str, list]:
    """1) Check that email is not empty
       2) Check that email format is correct
       3) Check that the domain name exist and is not a disposable one,
       if domain does not exist, suggest a correction in case of typing error
       4) Check that email exist in domain name
       If not, suggest a correction in case of typing error

    :param email: Input email
    :type email: str
    :param valid_domains: List of domains that have already been approved
    :type valid_domains: list
    :param disposable_domains: List of domains that are known to provide
    disposable addresses
    :type disposable_domains: list
    :param user_agents: List of user agents to pass when checking email 
    from website
    :type user_agents: list
    :return: Status code, correction suggestion, and updated valid domains list 
    in case of error
    :rtype: tuple[int, str, list]
    """
    email = infos[3]
    if is_empty(email):
        return 1, "", valid_domains
    elif not is_syntax_correct(email):
        return 2, "", valid_domains
    else:
        email_parts = split_email(email)
        domain_check, valid_domains = is_domain_valid(email_parts['domain'],
                                                      valid_domains,
                                                      disposable_domains)
        if domain_check == 3:
            return domain_check, "", valid_domains
        elif domain_check == 4:
            sugg_domain = correct_domain(email_parts['domain'],
                                         valid_domains)
            if len(sugg_domain) > 0:
                sugg_address = f"{email_parts['prefix']}@{sugg_domain}"
                email_check_sugg = email_exist(sugg_address, user_agents)
                if (email_check_sugg == 0) or (email_check_sugg == 5):
                    return 4, sugg_address, valid_domains
                else:
                    return 4, "", valid_domains
        else:
            email_check = email_exist(email, user_agents)
            if email_check == 2:
                return 2, "", valid_domains
            elif email_check == 5:
                return 5, "", valid_domains
            elif email_check == 6:
                sugg_prefix = correct_prefix(infos[1], infos[2],
                                             email_parts['prefix'])
                sugg_address = f"{sugg_prefix}@{email_parts['domain']}"
                email_check_sugg = email_exist(sugg_address, user_agents)
                if email_check_sugg == 0:
                    return 6, sugg_address, valid_domains
                else:
                    return 6, "", valid_domains
            else:
                return 0, "", valid_domains


def process_emails(df_email: DataFrame,
                   valid_domains: list,
                   disp_domains: list,
                   user_agents: list) -> tuple[DataFrame, list]:
    """Process all emails through pipeline
    Fill the dataframe with status code and suggestions
    Update valid domain list if possible

    :param df_email: Dataframe with name, surname and email
    :type df_email: DataFrame
    :param valid_domains: List of valid domains already known
    :type valid_domains: list
    :param disp_domains: List of domain known to provide disposable address
    :type disp_domains: list
    :param user_agents: List of user-agents
    :type user_agents: list
    :return: Updated email dataframe and valid domains list
    :rtype: tuple[DataFrame, list]
    """
    status_code = []
    suggestions = []
    for row in df_email.itertuples():
        code, suggestion, valid_domains, = pipeline_email(row,
                                                          valid_domains,
                                                          disp_domains,
                                                          user_agents)
        status_code.append(code)
        suggestions.append(suggestion)
    df_email['STATUS_CODE'] = status_code
    df_email['SUGGESTION'] = suggestions
    transco_code = {0: 'Email exist', 1: 'Email is empty',
                    2: 'Email syntax is incorrect',
                    3: 'Email is disposable',
                    4: 'Email domain does not exist',
                    5: 'Email is ok but cannot be verified',
                    6: 'Email not found in domain'}
    df_email['STATUS_LIB'] = df_email['STATUS_CODE'].map(transco_code)
    return df_email, valid_domains
