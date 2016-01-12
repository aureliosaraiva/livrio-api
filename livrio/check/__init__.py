from email_validator import validate_email, EmailSyntaxError, EmailUndeliverableError
import settings
import tldextract

from settings import redis_client

TYPE_ERROR = {
    'unknown':100,'syntax':101, 'local_short':102,'local_digit':103,
    'local_broadcast': 200,
    'mx_fail': 300,
    'domain_wifi': 400, 'domain_forbidden': 401,'domain_mailing_list': 402,
    'tld_forbidden': 500
}

def is_value_redis(name, value):
    return redis_client.sismember(name,value)

def is_gmail(local, domain):
    return domain == 'gmail.com' and (len(local) < 6 or len(local)>32)

def is_yahoo(local, domain):
    return (domain == 'yahho.com' or domain == 'yahho.com.br') and len(local) < 4

def is_hotmail(local, domain):
    return domain == 'hotmail.com' and len(local) < 5

def is_outlook(local, domain):
    return domain == 'outlook.com' and len(local) < 5

def check_syntax(email):
    try:
        v = validate_email(email, allow_smtputf8=False, check_deliverability=False)

        local = v['local']
        domain = v['domain']

        if local.isdigit():
            return (False, TYPE_ERROR['local_digit'])

        if len(local) == 1:
            return (False, TYPE_ERROR['local_short'])

        if is_gmail(local, domain):
            return (False, TYPE_ERROR['local_short'])

        if is_outlook(local, domain):
            return (False, TYPE_ERROR['local_short'])

        if is_hotmail(local, domain):
            return (False, TYPE_ERROR['local_short'])

        if is_yahoo(local, domain):
            return (False, TYPE_ERROR['local_short'])

        return (True, None)
    except EmailSyntaxError as e:
        return (False, TYPE_ERROR['syntax'])
    except:
        return (False, TYPE_ERROR['unknown'])


def check_local(email):
    try:
        local, domain = email.split('@')

        if is_value_redis('local_broadcast',local):
            return (False, TYPE_ERROR['local_broadcast'])

        return (True, None)
    except:
        return (False, TYPE_ERROR['unknown'])

def check_tld(email):
    local, domain = email.split('@')
    ext = tldextract.extract(domain)

    if is_value_redis('tld_forbidden',ext.suffix):
        return (False, TYPE_ERROR['tld_forbidden'])

    return (True, None)


def check_domain(email):
    try:
        local, domain = email.split('@')

        if is_value_redis('domain_wifi',domain):
            return (False, TYPE_ERROR['domain_wifi'])

        if is_value_redis('domain_forbidden',domain):
            return (False, TYPE_ERROR['domain_forbidden'])

        if is_value_redis('domain_mailing_list',domain):
            return (False, TYPE_ERROR['domain_mailing_list'])

        if len(domain.split(".")) >= 4:
            return (False, TYPE_ERROR['unknown'])

        return (True, None)
    except:
        return (False, TYPE_ERROR['unknown'])
    return None

def check_mx(email):
    try:
        local, domain = email.split('@')

        if is_value_redis('domain_mx_validated',domain):
            return (True, None)

        if is_value_redis('domain_mx_fail',domain):
            return (False, TYPE_ERROR['mx_fail'])

        if len(domain.split(".")) >= 4:
            settings.add_domain_mx_fail(domain)
            return (False, TYPE_ERROR['unknown'])

        print domain
        v = validate_email(email, allow_smtputf8=False, check_deliverability=True)
        
        settings.add_domain_mx_validated(domain)

        return (True, None)
    except EmailUndeliverableError as e:
        settings.add_domain_mx_fail(domain)
        return (False, TYPE_ERROR['mx_fail'])
    except:
        settings.add_domain_mx_fail(domain)
        return (False, TYPE_ERROR['unknown'])


def check_all(email):

    v = check_syntax(email)
    if not v[0]:
        return v

    v = check_local(email)
    if not v[0]:
        return v

    v = check_domain(email)
    if not v[0]:
        return v

    v = check_tld(email)
    if not v[0]:
        return v

    v = check_mx(email)
    if not v[0]:
        return v

    return (True, None)

