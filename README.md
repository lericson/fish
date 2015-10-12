Ever wanted to have animating fishes for progress bars in your command-line
script?

Ever thought about doing it but then realizing you have better things to do
with your time than to write meaningless ASCII animation programs?

Now you can have the best of both worlds: introducing ``fish``, the module that
makes any program look awesome and display useful data while churning away on
some good 'ole data.

Usage? Simple enough::

    >>> import fish
    >>> while churning:
    ...     churn_churn()
    ...     fish.animate()

As a boy, I often dreamed of birds going back and forth as progress bars, so I
decided to implement just that::

    >>> import fish
    >>> bird = fish.Bird()
    >>> while churning:
    ...     churn_churn()
    ...     bird.animate()

Want to show the current record number?::

    >>> from fish import ProgressFish
    >>> fish = ProgressFish()
    >>> for i, x in enumerate(churning):
    ...     churn_churn()
    ...     fish.animate(amount=i)

Want to show numeric progress when you know the total number?::

    >>> from fish import ProgressFish
    >>> fish = ProgressFish(total=len(data))
    >>> for i, datum in enumerate(data):
    ...     churn_churn()
    ...     fish.animate(amount=i)

`See a demo on YouTube`__.

__ http://www.youtube.com/watch?v=xYeG5CVTCmk

The default fish is a simple bass at a pretty good velocity for an ASCII fish.

Possibilities are endless here, gentlemen:

    The only limit is yourself.

    -- zombo.com

`Fork on GitHub`__

__ http://github.com/lericson/fish
