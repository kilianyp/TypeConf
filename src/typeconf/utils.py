def read_file_cfg(path):
    if path.endswith('.json'):
        import json
        with open(path, 'r') as f:
            return json.load(f)
    if path.endswith('.yaml'):
        # TODO requires extra dependency
        raise NotImplementedError
    if path.endswith('.py'):
        content = open(path).read()
        # https://stackoverflow.com/questions/1463306/how-does-exec-work-with-locals
        ldict = {}
        exec(content, globals(), ldict)
        return ldict['cfg']

    raise ValueError("Unknown file format %s" % path)
