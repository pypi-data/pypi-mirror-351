from dkist_fits_specifications.utils.spec_processors.expansion import ExpansionIndex


def expand_keys(naxis: int, keys: list[str]) -> list[str]:
    return_keys = []
    naxis_range = range(1, naxis + 1)
    n_expansion = ExpansionIndex(index="n", size=1, values=naxis_range)
    i_expansion = ExpansionIndex(index="i", size=1, values=naxis_range)
    j_expansion = ExpansionIndex(index="j", size=1, values=naxis_range)
    pp_expansion = ExpansionIndex(
        index="pp", size=2, values=[1, 10, 25, 75, 90, 95, 98, 99]
    )
    expansions = [n_expansion, i_expansion, j_expansion, pp_expansion]
    for key in keys:
        if "<" not in key:
            return [key]
        expanded_keys = [key]
        for expansion in expansions:
            expanded_keys.extend(expansion.generate(keys=expanded_keys))
        return_keys.extend([k for k in expanded_keys if "<" not in k])
    return return_keys
