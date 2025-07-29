import re

def sortvalue(values, reverse=False):
    def parse_size(s):
        s = s.strip().upper()
        match = re.match(r"([0-9.]+)\s*([KMGTPE]?B)", s)
        if not match:
            raise ValueError(f"Invalid size format: '{s}'")
        num, unit = match.groups()
        factor = {
            "B": 1,
            "KB": 1024,
            "MB": 1024**2,
            "GB": 1024**3,
            "TB": 1024**4,
            "PB": 1024**5,
            "EB": 1024**6,
        }
        return float(num) * factor[unit]

    return sorted(values, key=parse_size, reverse=reverse)
