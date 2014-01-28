from dateutil.parser import parse as parse_date


def date_to_epoch(s):
    return parse_date(s).strftime('%s')
