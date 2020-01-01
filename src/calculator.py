# Standard operators
def aod(x):
    return -x


def aor(x, y):
    return x * y


def asr(x, y):
    x += y
    return x


def bcr():
    for letter in 'Python':  # First Example
        if letter == 'h':
            break
    return letter


def cod(x):
    if not x:
        return False
    return True


def coi(x,):
    if x:
        return False
    return True


def crp():
    x = 1
    z = 'test'
    return x, z


class DDL:
    @ classmethod
    def ddl(cls):
        pass


class EHD:
    try:
        pass
    except NameError:
        pass


class EXS:
    try:
        pass
    except NameError:
        raise Exception("Temp")


class IHDSuper:
    y = 1


class IHD(IHDSuper):
    y = 2


class IODSuper:
    def foo(self):
        pass


class IOD(IODSuper):
    def foo(self):
        pass


class IOPSuper:
    def foo(self):
        pass


class IOP(IOPSuper):
    def foo(self):
        super().foo()
        x = 2


def lcr(x, y):
    if x or y:
        pass
    while x and y:
        pass


def lod(x):
    return ~ x


def lor(x, y):
    x & y
    x << y


def ror(x, y):
    if x < y:
        pass


class SCDSuper:
    def foo(self):
        pass


class SCD(SCDSuper):
    def foo(self):
        super().foo()


class SCISuper:
    def foo(self):
        pass


class SCI(SCISuper):
    def foo(self):
        pass


def sir(x, y):
    for x in y:
        pass


# Experimental mutation operators
def cdi(x, y):
    pass


def oil(x, y):
    pass


def ril(x, y):
    pass


def sdi(x, y):
    pass


def sdl(x, y):
    pass


class SVD:
    def svd(self):
        return self.x


def zil(x, y):
    pass

