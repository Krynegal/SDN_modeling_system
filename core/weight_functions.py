from core.main import bandwidth


def w_func1(x):
    return (x / bandwidth) + 1


def w_func2(x):
    return (x / bandwidth)**2 + 1


def ff_func(df, edge):
    return df[edge][0] * (df[edge][1] / bandwidth) if edge in df else 0


weight_funcs = {
    1: ff_func,
    2: ff_func,
}

