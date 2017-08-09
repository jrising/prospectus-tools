import cmd, sys, os, signal
import subprocess

processes = subprocess.Popen(['ps', '-Af'], stdout=subprocess.PIPE).stdout.read().split('\n')

mine = filter(lambda line: line[:7] == 'jrising' and 'python' in line, processes)
pids = map(lambda line: line.split()[1], mine)
commands = map(lambda line: line[line.index('python'):], mine)
unique = set(commands)
unique.discard('python processes.py')

for command in unique:
    print commands.count(command), command

class Manager(cmd.Cmd):
    def do_kill(self, arg):
        for pid in [int(pids[ii]) for ii in range(len(commands)) if commands[ii] == arg]:
            print "Killing %d" % pid
            os.kill(pid, signal.SIGTERM)

    def complete_kill(self, text, line, begidx, endidx):
        possibles = list(unique)
        for chunk in line.split()[1:-1]:
            possibles = [possible[len(chunk)+1:] for possible in possibles if possible[:len(chunk)] == chunk]

        return filter(lambda possible: possible[:len(text)] == text, possibles)

Manager().cmdloop()
