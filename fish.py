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
    def __init__(self, velocity=10, world_length=79, outfile=sys.stderr, total=None):
        if total > 0:
            pad = len(str(total))*2
            pad += 6
            world_length = world_length - pad
        self.worldstep = self.make_worldstepper()
        self.velocity = velocity
        self.world_length = world_length
        self.outfile = outfile
        self.last_hash = 0
        self.total = total

    def animate(self, outfile=None, force=False, amount=''):
        step = self.worldstep.next()
        # Refit the world so that we can move along an axis and not worry about
        # overflowing
        actual_length = self.world_length - self.own_length
        if amount and self.total:
            amount_string = '%s%% %s/%s' % \
                (str(int(round(amount/float(self.total)*100))).rjust(3), \
                str(amount).rjust(len(str(self.total))), self.total)
            pos = (amount/float(self.total))*float(actual_length)
            pos += actual_length #so it moves left to right
        else:
            amount_string = '%s' % amount
            # As there are two directions we pretend the world is twice as large as
            # it really is
            pos = (self.velocity * step) % (actual_length * 2)
        reverse = pos < actual_length
        pos = int(round(abs(pos - actual_length), 0))
        fish = self.render(reverse=reverse)
        of = outfile or self.outfile
        curr_hash = force or hash((of, pos, fish, amount_string))
        if force or curr_hash != self.last_hash:
            lead = " " * (pos)
            trail = " " * (self.world_length - self.own_length - pos)
            of.write("\x1b[2K\r" + lead + fish + trail + amount_string + "\r")
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
    try:
        total = int(sys.argv[1])
        f = Fish(total=total)
        for i in range(total):
            f.animate(amount=i+1)
            time.sleep(0.1)
    except IndexError: 
        while True:
            animate()
            time.sleep(0.1)
    
