import dagstream


def funcA():
    return None

def funcB():
    return None


stream = dagstream.DagStream()
A_val, B_val = stream.emplace(funcA, funcB)

A_val.precede(B_val)


stream.prepare()

while not stream.is_active:
    for val in stream.get_ready():
        print(val.name)
        stream.done(val)