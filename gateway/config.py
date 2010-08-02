from constants import SITIOS, ROBOTS

slaves = {}
robots = {}

from twisted.internet.defer import Deferred

class FakeTransport(object):
    def __getattr__(self, name):
        return lambda *a, **kw: Deferred()

class Sitio(object):
    def __init__(self, ccc, online=False):
        self.ccc = ccc
        self.online = online
        self.transport = FakeTransport()

class Robot(object):
    def __init__(self, online=True):
        self.online = online
        self.errores = 0

for ccc in SITIOS:
    slaves[ccc] = Sitio(ccc)
    robots[ccc] = [Robot() for x in range(ROBOTS[ccc])]

