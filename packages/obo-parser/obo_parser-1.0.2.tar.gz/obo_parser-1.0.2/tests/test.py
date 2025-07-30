from collections import defaultdict


def read_file(file_path):
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if line:
                yield line


header = True
metadata = defaultdict(list)
term = {}
for line in read_file('tests/hp.obo'):
    if line == '[Term]':
        header = False
        if term:
            print(term)
        term = {}
        continue
    if line == '[Typedef]':
        print(term)
        break

    if header:
        key, value = line.split(': ', 1)
        if ' ' in value:
            metadata[key].append(value)
        else:
            metadata[key] = value

    key, value = line.split(': ', 1)
    term[key] = value

