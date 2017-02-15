# mapping from numeric value to entry
keycodes = dict()

with open('keycodes.txt') as f:
    for l in f.readlines():
        l = l[:-1]  # remove newline
        if l.startswith('#'):
            continue
        comps = l.split('\t')

        assert len(comps) == 3

        name = comps[0]
        numeric = int(comps[1], 16)     # they're in hex
        description = comps[2]

        keycodes[numeric] = {'name': name, 'description': description}
