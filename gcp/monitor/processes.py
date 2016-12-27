import subprocess

processes = subprocess.Popen(['ps', '-Af'], stdout=subprocess.PIPE).stdout.read().split('\n')

mine = filter(lambda line: line[:7] == 'jrising' and 'python' in line, processes)
commands = map(lambda line: line[line.index('python'):], mine)
unique = set(commands)
for command in unique:
    print commands.count(command), command


