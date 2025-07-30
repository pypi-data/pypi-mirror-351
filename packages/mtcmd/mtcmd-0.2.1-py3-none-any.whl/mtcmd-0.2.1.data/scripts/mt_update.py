#!python


from importlib import metadata as im
from subprocess import call

packages = [dist.name for dist in im.distributions()]
packages = [x for x in packages if x.startswith('mt')]
call("pipi -U " + ' '.join(packages), shell=True)
