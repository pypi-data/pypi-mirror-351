def sortvalue(values, reverse=False):
    def parse_size(s):
        num, unit = s.strip().split()
        factor = {
            "B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3,
            "TB": 1024**4, "PB": 1024**5
        }
        unit = unit.upper().replace("B", "") + "B"  # Normalize unit
        return float(num) * factor.get(unit, 1)

    return sorted(values, key=parse_size, reverse=reverse)
