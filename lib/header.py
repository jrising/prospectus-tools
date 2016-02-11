import re, datetime

endheader = "##########\n"

def dated_version(prefix):
    return prefix + '.' + str(datetime.date.today())

def write_headinfo(fp, headinfo):
    write(fp, headinfo['oneline'], headinfo['version'], headinfo.get('dependencies', []), headinfo['variables'],
          headinfo['sources'], headinfo.get('description', None))

def write(fp, oneline, version, dependencies, variables, sources=None, description=None, prefix="# "):
    """Writes the common header.
online and version are short strings.
dependencies is a list of versions.
variables is a dictionary of name => tuple (short description, units).
sources is a dictionary of name => one-line string.
description can be many lines or missing."""

    fp.write(prefix + oneline + "\n")
    fp.write(prefix + "\n")
    fp.write(prefix + "Version: " + version + "\n")
    if dependencies:
        fp.write(prefix + "Dependencies: " + ', '.join(dependencies) + "\n")
    fp.write(prefix + "Variables:\n")
    if isinstance(variables, str):
        fp.write(prefix + "   " + variables + "\n")
    else:
        for name in variables:
            fp.write(prefix + "   " + name + ": " + variables[name][0] + " [" + variables[name][1] + "]\n")
    if sources is not None:
        fp.write(prefix + "Sources:\n")
        for name in sources:
            fp.write(prefix + "   " + name + ": " + sources[name] + "\n")

    if description:
        fp.write(prefix + "\n")
        for line in description.split('\n'):
            fp.write(prefix + line + "\n")
    if prefix != '':
        fp.write(endheader)

def deparse(fp, dependencies):
    header = parse(fp)

    if 'version' in header and header['version'] not in dependencies:
        dependencies.append(header['version'])

    return fp

def parse(fp):
    if isinstance(fp, str):
        with open(fp, 'r') as fp2:
            return parse(fp2)

    header = {}
    header['oneline'] = fp.next()[2:]

    addcall = None
    for line in fp:
        if line == endheader:
            break

        if line.strip() == "#":
            if 'oneline' in header and 'version' in header and 'dependencies' in header and 'variables' in header and 'sources' in header:
                break
            continue

        chunks = line[2:].split(':')
        title = chunks[0].strip().lower()
        if title == 'version':
            header['version'] = chunks[1].strip()
            addcall = None
        elif title == 'dependencies':
            header['dependencies'] = map(lambda s: s.strip(), chunks[1].split(','))
            addcall = None
        elif title == 'variables':
            header['variables'] = {}
            addcall = lambda name, info: header['variables'].__setitem__(name, re.match("([^\\[]+)\s+\\[([^\\]]+)\\]", info))
        elif title == 'sources':
            header['sources'] = {}
            addcall = lambda name, info: header['sources'].__setitem__(name, info)
        elif addcall is not None and len(chunks) > 1:
            addcall(title, chunks[1])

    if line != endheader:
        description = []
        for line in fp:
            if line == endheader:
                break

            description.append(line)

        header['description'] = ''.join(description)

    return header

def add_header(filename_in, filename_out, oneline, version, dependencies, variables, sources, description=None):
    with open(filename_in, 'r') as fp_in:
        with open(filename_out, 'w') as fp_out:
            write(fp_out, oneline, version, dependencies, variables, sources, description)
            for line in fp_in:
                fp_out.write(line)

if __name__ == '__main__':
    import sys
    import readline

    def rlinput(prompt, prefill=''):
        readline.set_startup_hook(lambda: readline.insert_text(prefill))
        try:
            return raw_input(prompt)
        finally:
            readline.set_startup_hook()

    filename_in = sys.argv[1]

    if filename_in[-4:].lower() == '.fgh':
        filename_out = filename_in
        print "Output file: ", filename_out
        filename_in = None
    else:
        print "Input File: ", filename_in
        filename_out = rlinput("Output File: ", filename_in)

    oneline = rlinput("One line description: ")
    version = rlinput("Version: ")

    print "Enter the dependencies (blank to finish):"
    dependencies = []
    while True:
        dependency = rlinput("Version: ")
        if not dependency:
            break
        dependencies.append(dependency)

    print "Define the variables (blank to finish):"
    variables = {}
    while True:
        name = rlinput("Variable Name: ")
        if not name:
            break

        desc = rlinput("Short description: ")
        unit = rlinput("Units: ")
        variables[name] = (desc, unit)

    print "Define the sources (blank to finish):"
    sources = {}
    while True:
        name = rlinput("Source Name: ")
        if not name:
            break

        desc = rlinput("Short description: ")
        sources[name] = desc

    print "Enter a description (type Ctrl-D on a blank line to finish):"
    description = '\n'.join(sys.stdin.readlines())
    if not description.strip():
        description = None

    if filename_in is not None:
        add_header(filename_in, filename_out, oneline, version, dependencies, variables, sources, description)
    else:
        with open(filename_out, 'w') as fp_out:
            write(fp_out, oneline, version, dependencies, variables, sources, description)

