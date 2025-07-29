def fmt_val(val, shorten=True):
    """Format a value for inclusion in aninformative text string."""
    val = repr(val)
    max = 50
    if shorten:
        if len(val) > max:
            close = val[-1]
            stop = max - 4
            val = val[0:stop] + "..."
            if close in (">", "'", '"', "]", "}", ")"):
                val = val + close
    return val


def fmt_dict_vals(dict_vals, shorten=True):
    """
    Returns list of key=val pairs formatted
    for inclusion in an informative text string.
    """
    items = dict_vals.items()
    if not items:
        return [fmt_val(None, shorten=shorten)]
    return ["%s=%s" % (k, fmt_val(v, shorten=shorten)) for k, v in items]
