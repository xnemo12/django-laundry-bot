def to_pair_list(t, size=2):
    it = iter(t)
    return zip(*[it]*size)