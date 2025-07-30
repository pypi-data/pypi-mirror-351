"""
This file contains functions for different python and django version compatibility
"""
import datetime
import re
import sys
from datetime import timezone

from django.utils.timezone import make_aware

if hasattr(re, 'Pattern'):
    PatternType = re.Pattern
else:
    PatternType = re._pattern_type  # noqa

# six.string_types replacement in order to remove dependency
string_types = (str,) if sys.version_info[0] == 3 else (str, unicode)  # noqa F821


def to_timestamp(dt):  # type: (datetime.datetime) -> float
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        dt = make_aware(dt, timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)

    # dt.timestamp() does not work before python 3.3
    if hasattr(dt, 'timestamp'):
        return dt.timestamp()
    else:
        return (dt - datetime.datetime(1970, 1, 1, 0, 0, 0, tzinfo=timezone.utc)).total_seconds()
