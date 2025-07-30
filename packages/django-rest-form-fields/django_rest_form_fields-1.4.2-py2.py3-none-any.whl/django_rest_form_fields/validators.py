import re
from django.core.validators import URLValidator

try:
    # This attribute has been moved from URLValidator to DomainNameValidator in django 5.2
    from django.core.validators import DomainNameValidator

    ul = getattr(DomainNameValidator, "ul", getattr(URLValidator, "ul", None))
except ImportError:
    ul = URLValidator.ul



class URLValidatorWithUnderscoreDomain(URLValidator):
    hostname_re = r'[a-z' + ul + r'0-9](?:[a-z' + ul + r'0-9-_]{0,61}[a-z' + ul + r'0-9])?'
    host_re = '(' + hostname_re + URLValidator.domain_re + URLValidator.tld_re + '|localhost)'

    regex = re.compile(
        r'^(?:[a-z0-9.+-]*)://'  # scheme is validated separately
        r'(?:[^\s:@/]+(?::[^\s:@/]*)?@)?'  # user:pass authentication
        r'(?:' + URLValidator.ipv4_re + '|' + URLValidator.ipv6_re + '|' + host_re + ')'
        r'(?::\d{2,5})?'  # port
        r'(?:[/?#][^\s]*)?'  # resource path
        r'\Z', re.IGNORECASE
    )
