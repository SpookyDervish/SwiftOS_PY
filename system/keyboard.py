import os, sys, re


def getcapslock():
    s = os.popen('xset -q').read()
    if re.search('Caps Lock:\s+on', s):
        return True
    else:
        return False