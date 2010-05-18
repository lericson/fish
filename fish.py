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
import string

from struct import unpack
from fcntl import ioctl
from termios import TIOCGWINSZ

from itertools import cycle, count

def get_term_width():
    """Get terminal width or None."""
    for fp in sys.stdin, sys.stdout, sys.stderr:
        try:
            return unpack("hh", ioctl(fp.fileno(), TIOCGWINSZ, "    "))[1]
        except IOError:
            continue

class ANSIControl(object):
    def __init__(self, outfile=sys.stderr, flush=True):
        self.outfile = outfile
        self.flush = flush

    def ansi(self, command):
        self.outfile.write("\x1b[%s" % command)
        if self.flush:
            self.outfile.flush()

    def clear_line_right(self): self.ansi("0K\r")
    def clear_line_left(self): self.ansi("1K\r")
    def clear_line_whole(self): self.ansi("2K\r")
    def clear_forward(self): self.ansi("0J")
    def clear_backward(self): self.ansi("1J")
    def clear_whole(self): self.ansi("2J")
    def save_cursor(self): self.ansi("s")
    def restore_cursor(self): self.ansi("u")
    def move_up(self, n): self.ansi("%dF" % n)
    def move_down(self, n): self.ansi("%dE" % n)

class SwimFishBase(object):
    def __init__(self, velocity=10, world_length=None, outfile=sys.stderr):
        if not world_length:
            world_length = get_term_width() or 79
        self.worldstep = self.make_worldstepper()
        self.velocity = velocity
        self.world_length = world_length
        self.outfile = outfile
        self.ansi = ANSIControl(outfile=outfile)
        self.last_hash = 0

    def animate(self, outfile=None, force=False):
        step = self.worldstep.next()
        # Refit the world so that we can move along an axis and not worry about
        # overflowing
        actual_length = self.world_length - self.own_length
        # As there are two directions we pretend the world is twice as large as
        # it really is, then handle the overflow
        pos = (self.velocity * step) % (actual_length * 2)
        reverse = pos < actual_length
        pos = int(round(abs(pos - actual_length), 0))
        fish = self.render(step=step, reverse=reverse)
        of = outfile or self.outfile
        curr_hash = force or hash((of, pos, "".join(fish)))
        if force or curr_hash != self.last_hash:
            self.print_fish(of, pos, fish)
            of.flush()
            self.last_hash = curr_hash

    def print_fish(self, of, pos, fish):
        raise NotImplementedError("you must choose a printer type")

class SingleLineFishPrinter(SwimFishBase):
    def print_fish(self, of, pos, fish):
        lead = " " * pos
        trail = " " * (self.world_length - self.own_length - pos)
        self.ansi.clear_line_whole()
        assert len(fish) == 1
        of.write(lead + fish[0] + trail + "\r")

class MultiLineFishPrinter(SwimFishBase):
    _printed = False

    def __init__(self, *args, **kwds):
        super(MultiLineFishPrinter, self).__init__(*args, **kwds)
        self.reset()

    def reset(self):
        """Call this when reusing the animation in a new place"""
        self._printed = False

    def _restore_cursor(self, lines):
        if self._printed:
            self.ansi.move_up(lines)
        self._printed = True

    def print_fish(self, of, pos, fish):
        lead = " " * pos
        trail = " " * (self.world_length - self.own_length - pos)
        self._restore_cursor(len(fish))
        self.ansi.clear_forward()
        for line in fish:
            of.write(lead + line + trail + "\n")

class ProgressableFishBase(SwimFishBase):
    """Progressing fish, only compatible with single-line fish"""

    def __init__(self, *args, **kwds):
        total = kwds.pop("total", None)
        super(ProgressableFishBase, self).__init__(*args, **kwds)
        if total:
            # `pad` is the length required for the progress indicator,
            # It, at its longest, is `100% 123/123`
            pad = len(str(total)) * 2
            pad += 6
            self.world_length -= pad
        self.total = total

    def animate(self, *args, **kwds):
        prev_amount = getattr(self, "amount", None)
        self.amount = kwds.pop("amount", None)
        if self.amount != prev_amount:
            kwds["force"] = True
        return super(ProgressableFishBase, self).animate(*args, **kwds)

    def print_fish(self, of, pos, fish):
        if not self.amount:
            return super(ProgressableFishBase, self).print_fish(of, pos, fish)

        # Get the progress text
        if self.total:
            part = self.amount / float(self.total)
            done_text = str(self.amount).rjust(len(str(self.total)))
            progress = "%3.d%% %s/%d" % (part * 100, done_text, self.total)
        else:
            progress = str(amount)

        lead = " " * pos
        trail = " " * (self.world_length - self.own_length - pos)
        self.ansi.clear_line_whole()
        assert len(fish) == 1
        of.write(lead + fish[0] + trail + progress + "\r")

class BassLook(SwimFishBase):
    def render(self, step, reverse=False):
        return ["<'((<" if reverse else ">))'>"]

    own_length = len(">))'>")

class SalmonLook(SwimFishBase):
    def render(self, step, reverse=False):
        return ["<*}}}><" if reverse else "><{{{*>"]

def docstring2lines(ds):
    return filter(None, ds.split("\n"))
rev_trans = string.maketrans(r"/\<>76", r"\/></9")
def ascii_rev(ascii):
    return [line.translate(rev_trans)[::-1] for line in ascii]

class BirdLook(SwimFishBase):
    # ASCII credit: "jgs"
    bird = r"""
           ___     
       _,-' ______ 
     .'  .-'  ____7
    /   /   ___7   
  _|   /  ___7     
>(')\ | ___7       
  \\/     \_______ 
  '        _======>
  `'----\\`        
"""
    bird = docstring2lines(bird)
    bird_rev = ascii_rev(bird)

    def render(self, step, reverse=False):
        return self.bird if reverse else self.bird_rev

    own_length = len(bird[0])

class SmallBirdLook(SwimFishBase):
    # ASCII art crediT: jgs
    bird = docstring2lines("""
     _ 
\. _(9>
 \==_) 
  -'=  
""")

    bird_rev = docstring2lines("""
 _     
<6)_ ,/
 (_==/ 
  ='-  
""")

    def render(self, step, reverse=False):
        return self.bird_rev if reverse else self.bird

    own_length = len(bird[0])

class SwimFishNoSync(SwimFishBase):
    @classmethod
    def make_worldstepper(cls):
        return count()

class SwimFishTimeSync(SwimFishBase):
    @classmethod
    def make_worldstepper(cls):
        return iter(time.time, None)

class Fish(ProgressableFishBase, SingleLineFishPrinter,
           SwimFishTimeSync, BassLook):
    """The default swimming fish, the one you very likely want to use.
    See module-level documentation.
    """

class Bird(MultiLineFishPrinter, SwimFishTimeSync, BirdLook):
    """What? A bird?"""

default_fish = Fish()
animate = default_fish.animate

if __name__ == "__main__":
    import signal
    signal.signal(signal.SIGINT, lambda *a: sys.exit(0))

    fish = default_fish
    amounts = None

    if sys.argv[1:]:
        if sys.argv[1] == "--bird":
            fish = Bird()
        else:
            total = int(sys.argv[1])
            fish = Fish(total=total)
            amounts = xrange(1, total + 1)

    if amounts:
        for amount in amounts:
            fish.animate(amount=amount)
            time.sleep(0.1)
    else:
        while True:
            fish.animate()
            time.sleep(0.1)
