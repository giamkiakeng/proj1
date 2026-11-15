"""minit.py -- mcopy.Model with another initial state of the first cell.

model_class(init) returns a subclass of Model whose lines start from X L ... L, where X is the working state
with index init (1 = G is the default of mcopy.py).  The class conditions of mcopy.py (--b1, --b3w, --b4, --noghw,
...) always speak about the state G; with init = 2 the first cell starts in state A, so that G is a stable,
firing state different from the initial state of the general."""
from mcopy import Model

def model_class(init):
    if init == 1:
        return Model
    class ModelInit(Model):
        INIT = init
        def H(self, t, i):
            if t == 0 and i == 1:
                return self.INIT
            return Model.H(self, t, i)
    return ModelInit
