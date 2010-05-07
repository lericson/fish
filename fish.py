"""
    Swimming fishes progress indicator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Well, what can you say really? It's a swimming fish that animates when you
    call a certain function. Simple as that.

    How to use:

    .. code-block:: python

       import fish

       for datum_to_churn in data:
           fish.animate()
           churn_churn(datum_to_churn)
"""

import sys
import time
from itertools import count

class SwimFishBase(object):
    def __init__(self, velocity=10, world_length=79, outfile=sys.stderr):
        self.worldstep = self.make_worldstepper()
        self.velocity = velocity
        self.world_length = world_length
        self.outfile = outfile
        self.last_hash = 0

    def animate(self, outfile=None, force=False):
        step = self.worldstep.next()
        # Refit the world so that we can move along an axis and not worry about
        # overflowing
        actual_length = self.world_length - self.own_length
        # As there are two directions we pretend the world is twice as large as
        # it really is
        pos = (self.velocity * step) % (self.world_length * 2)
        reverse = pos < self.world_length
        pos = int(round(abs(pos - self.world_length), 0))
        fish = self.render(reverse=reverse)
        of = outfile or self.outfile
        curr_hash = force or hash((of, pos, fish))
        if force or curr_hash != self.last_hash:
            lead = " " * pos
            trail = " " * (self.world_length - len(fish) - pos)
            of.write("\x1b[2K\r" + lead + fish + trail + "\r")
            of.flush()
            self.last_hash = curr_hash

class BassLook(SwimFishBase):
    def render(self, reverse=False):
        return "<'((<" if reverse else ">))'>"

    own_length = len(">))'>")

class SalmonLook(SwimFishBase):
    def render(self, reverse=False):
        return "<*}}}><" if reverse else "><{{{*>"

    own_length = len("><{{{*>")

class SwimFishNoSync(SwimFishBase):
    @classmethod
    def make_worldstepper(cls):
        return count()

class SwimFishTimeSync(SwimFishBase):
    @classmethod
    def make_worldstepper(cls):
        return iter(time.time, None)

class Fish(SwimFishTimeSync, BassLook):
    """The default swimming fish, the one you very likely want to use.
    See module-level documentation.
    """

default_fish = Fish()
animate = default_fish.animate

if __name__ == "__main__":
    while True:
        animate()
        time.sleep(0.1)
