# -*- coding:utf-8 -*-
"""Classes for representing angles.

This module provides three classes for representing angles: `Angle`,
`AlphaAngle` and `DeltaAngle`. The first is for representing generic
angles. The second is for representing RA-like longitudinal angles and
the third is for representing Dec-like latitudinal angles.

An angle object can be initialized and can provide its value in various
units, it can normalize its value into appropriate range, and it can
provide string representations of itself.

This module also provides an `AngularPosition` class which can be used
for representing points on a sphere. It uses an `AlphaAngle` instance
for storing the longitudinal angle and a `DeltaAngle` instance for
storing the latitudinal angle. It can calcuate the separation to
another point on the sphere. It can also calculate the bearing of
another point on the sphere. The results from separation and bearing
agree with those from the SLALIB (pyslalib) library.

See docstrings of `Angle`, `AlphaAngle`, `DeltaAngle` and
`AngularPosition` for documentation and examples.

The methods of classes call various functions defined in this
module. If needed these functions can be called directly for performing
various calculations. Functions include those for parsing sexagesimal
strings, creating string representations of angles, converting angles
between various units, normalizing angles into a given range and
others. Normalization can be performed in two different ways: one like
that needed for RA-like angles [0, 360.0) or [0, 2π] or [0, 24.0) and
one like that needed for Dec-like angles [-90, 90] or [-π/2, π/2].


:author: Prasanth Nair
:contact: prasanthhn@gmail.com
:license: BSD (http://www.opensource.org/licenses/bsd-license.php)
"""
import warnings
import math
import re


def r2d(r):
    """Convert radians to degrees. Calls math.degrees."""
    return math.degrees(r)


def d2r(d):
    """Convert degrees to radians. Calls math.radians."""
    return math.radians(d)


def h2d(h):
    """Convert hours into degrees."""
    return h * 15.0


def d2h(d):
    """Convert degrees into hours."""

    return d * (24.0 / 360.0)


def arcs2d(arcs):
    """Convert arcseconds into degrees."""
    return arcs / 3600.0


def d2arcs(d):
    """Convert degrees into arcseconds."""
    return d * 3600.0


def h2r(h):
    """Convert hours to radians."""
    return d2r(h2d(h))


def r2h(r):
    """Convert radians into hours."""
    return d2h(r2d(r))


def arcs2r(arcs):
    """Convert arcseconds to radians."""
    return d2r(arcs2d(arcs))


def r2arcs(r):
    """Convert radians to arcseconds."""
    return d2arcs(r2d(r))


def arcs2h(arcs):
    """Convert arcseconds to hours."""
    return d2h(arcs2d(arcs))


def h2arcs(h):
    """Convert hours to arcseconds."""
    return d2arcs(h2d(h))


def normalize(num, lower=0.0, upper=360.0, b=False):
    """Normalize number to range [lower, upper) or [lower, upper].

    Parameters
    ----------
    num : float
        The number to be normalized.
    lower : float
        Lower limit of range. Default is 0.0.
    upper : float
        Upper limit of range. Default is 360.0.
    b : bool
        Type of normalization. See notes.

    Returns
    -------
    n : float
        A number in the range [lower, upper) or [lower, upper].

    Raises
    ------
    ValueError
      If lower >= upper.

    Notes
    -----
    If the keyword `b == False`, the default, then the normalization
    is done in the following way. Consider the numbers to be arranged
    in a circle, with the lower and upper marks sitting on top of each
    other. Moving past one limit, takes the number into the beginning
    of the other end. For example, if range is [0 - 360), then 361
    becomes 1. Negative numbers move from higher to lower
    numbers. So, -1 normalized to [0 - 360) becomes 359.

    If the keyword `b == True` then the given number is considered to
    "bounce" between the two limits. So, -91 normalized to [-90, 90],
    becomes -89, instead of 89. In this case the range is [lower,
    upper]. This code is based on the function `fmt_delta` of `TPM`.

    Range must be symmetric about 0 or lower == 0.

    Examples
    --------
    >>> normalize(-270,-180,180)
    90
    >>> import math
    >>> math.degrees(normalize(-2*math.pi,-math.pi,math.pi))
    0.0
    >>> normalize(181,-180,180)
    -179
    >>> normalize(-180,0,360)
    180
    >>> normalize(36,0,24)
    12
    >>> normalize(368.5,-180,180)
    8.5
    >>> normalize(-100, -90, 90, b=True)
    -80.0
    >>> normalize(100, -90, 90, b=True)
    80.0
    >>> normalize(181, -90, 90, b=True)
    -1.0
    >>> normalize(270, -90, 90, b=True)
    -90.0
    """
    from math import floor, ceil
    # abs(num + upper) and abs(num - lower) are needed, instead of
    # abs(num), since the lower and upper limits need not be 0. We need
    # to add half size of the range, so that the final result is lower +
    # <value> or upper - <value>, respectively.
    res = num
    if not b:
        if lower >= upper:
            raise ValueError("Invalid lower and upper limits: (%s, %s)" %
                             (lower, upper))

        res = num
        if num > upper or num == lower:
            num = lower + abs(num + upper) % (abs(lower) + abs(upper))
        if num < lower or num == upper:
            num = upper - abs(num - lower) % (abs(lower) + abs(upper))

        res = lower if res == upper else num
    else:
        total_length = abs(lower) + abs(upper)
        if num < -total_length:
            num += ceil(num / (-2 * total_length)) * 2 * total_length
        if num > total_length:
            num -= floor(num / (2 * total_length)) * 2 * total_length
        if num > upper:
            num = total_length - num
        if num < lower:
            num = -total_length - num

        res = num * 1.0  # Make all numbers float, to be consistent

    return res


def d2d(d):
    """Normalize angle in degree to [0, 360)."""
    return normalize(d, 0, 360)


def h2h(h):
    """Normalize angle in hours to [0, 24.0)."""
    return normalize(h, 0, 24)


def r2r(r):
    """Normalize angle in radians to [0, 2π)."""
    return normalize(r, 0, 2 * math.pi)


def deci2sexa(deci, pre=3, trunc=False):
    """Returns the sexagesimal representation of a decimal number.

    Parameters
    ----------
    deci : float
        Decimal number to be converted into sexagesimal.
    pre : int
        Number of digits in the final sexagesimal part.
    trunc : bool
        If True then the last part of the sexagesimal number is
        truncated and not rounded.

    Returns
    -------
    s : 4 element tuple; (int, int, int, float)
        A tuple of sign and the three parts of the sexagesimal
        number. Sign is 1 for positive and -1 for negative values. The
        sign applies to the whole angle and not to any single part,
        i.e., all parts are positive and the sign multiplies the
        angle. The first and second parts of the sexagesimal number are
        integers and the last part is a float.

    Notes
    -----
    The given decimal number `deci` is converted into a sexagesimal
    number. The last part of the sexagesimal number is rounded to `pre`
    number of decimal points. If `trunc == True` then instead of
    rounding, the last part is truncated.

    The returned sign, first element of tuple, applies to the whole
    number and not just to a single part.

    Examples
    --------
    >>> deci2sexa(-11.2345678)
    (-1, 11, 14, 4.444)
    >>> deci2sexa(-11.2345678,pre=3)
    (-1, 11, 14, 4.444)
    >>> x = deci2sexa(-11.2345678,pre=1)
    >>> assert x == (-1, 11, 14, 4.4)
    >>> deci2sexa(-11.2345678,pre=0)
    (-1, 11, 14, 4.0)
    >>> deci2sexa(-11.2345678,pre=-1)
    (-1, 11, 14, 0.0)
    >>> x=deci2sexa(12.989987,pre=5)
    >>> assert x[0] == 1
    >>> assert x[1] == 12
    >>> assert x[2] == 59
    >>> assert x[3] == 23.9532
    >>> x = deci2sexa(12.989987,pre=5,trunc=True)
    >>> assert x == (1, 12, 59, 23.95319)
    >>> x = deci2sexa(12.989987,pre=4)
    >>> assert x == (1, 12, 59, 23.9532)
    >>> x = deci2sexa(12.989987,pre=4,trunc=True)
    >>> assert x == (1, 12, 59, 23.9531)
    """
    sign = 1
    if deci < 0:
        deci = abs(deci)
        sign = -1

    hd, f1 = divmod(deci, 1)
    mm, f2 = divmod(f1 * 60.0, 1)
    sf = f2 * 60.0

    # Find the seconds part to required precision.
    fp = 10**pre
    if trunc:
        ss, _ = divmod(sf * fp, 1)
    else:
        ss = round(sf * fp, 0)

    ss = int(ss)

    # If ss is 60 to given precision then update mm, and if necessary
    # hd.
    if ss == 60 * fp:
        mm += 1
        ss = 0
    if mm == 60:
        hd += 1
        mm = 0

    ss /= float(fp)
    # hd and mm parts are integer values but of type float
    return (sign, int(hd), int(mm), ss)


def sexa2deci(sign, hd, mm, ss, todeg=False):
    """Combine sexagesimal components into a decimal number.

    Parameters
    ----------
    sign : int
        Sign of the number: 1 for +ve, -1 for negative.
    hd : float
        The hour or degree like part.
    mm : float
        The minute or arc-minute like part.
    ss : float
        The second or arc-second like part.
    todeg : bool
        If True then convert to deg., assuming value is in hours.

    Returns
    -------
    d : float
        The decimal equivalent of the sexagesimal number.

    Raises
    ------
    ValueError
        This exception is raised if `sign` is not -1 or 1.

    Notes
    -----
    The angle returned is::

      sign * (hd + mm / 60.0 + ss / 3600.0)

    In sexagesimal notation the sign applies to the whole quantity and
    not to each part separately. So the `sign` is asked separately, and
    applied to the whole quantity.

    If the sexagesimal quantity is in hours, then we frequently want to
    convert it into degrees. If the `todeg == True` then the given
    value is assumed to be in hours, and the returned value will be in
    degrees.

    Examples
    --------
    >>> d = sexa2deci(1,12,0,0.0)
    >>> print d
    12.0
    >>> d = sexa2deci(1,12,0,0.0,todeg=True)
    >>> d
    180.0
    >>> x = sexa2deci(1,9,12.456,0.0)
    >>> assert round(x,4) == 9.2076
    >>> x  = sexa2deci(1,11,30,27.0)
    >>> assert round(x, 4) == 11.5075
    """
    divisors = [1.0, 60.0, 3600.0]
    d = 0.0
    # sexages[0] is sign.
    if sign not in (-1, 1):
        raise ValueError("Sign has to be -1 or 1.")

    sexages = [sign, hd, mm, ss]
    for i, divis in zip(sexages[1:], divisors):
        d += i / divis

    # Add proper sign.
    d *= sexages[0]

    if todeg:
        d = h2d(d)

    return d


def fmt_angle(val, s1=" ", s2=" ", s3=" ", pre=3, trunc=False,
              lower=0, upper=0, b=False):
    """Return sexagesimal string of given angle in degrees or hours.

    Parameters
    ----------
    val : float
        The angle (in degrees or hours) that is to be converted into a
        string.
    s1 : str
        Character to be used between the first and second parts of the
        the sexagesimal representation.
    s2 : str
        Character to be used between the second and third parts of the
        the sexagesimal representation.
    s3 : str
        Character to be used after the third part of the sexagesimal
        representation.
    pre : int
        Number of decimal places to use for the last part of the
        sexagesimal representation. This can be negative.
    trunc : bool
        If True then the third part of the sexagesimal number os
        truncated to `pre` decimal places, instead of rounding.
    lower, upper : float
        If `lower` and `upper` are given then the given value is
        normalized into the this range before converting to sexagesimal
        string.
    b : bool
        This affect how the normalization is performed. See notes. This
        works exactly like that for the function `normalize()`.

    See also
    --------
    normalize
    deci2sexa

    Examples
    --------
    >>> angle.fmt_angle(12.3456)
    '+12 20 44.160 '
    >>> angle.fmt_angle(12.345678923)
    '+12 20 44.444 '
    >>> angle.fmt_angle(12.345678923, pre=4)
    '+12 20 44.4441 '
    >>> angle.fmt_angle(12.345678923, pre=5)
    '+12 20 44.44412 '
    >>> angle.fmt_angle(12.345678923, s1="HH ", s2="MM ", s3="SS ")
    '+12HH 20MM 44.444SS '
    >>> angle.fmt_angle(12.345678923, s1="DD ", s2="MM ", s3="SS ")
    '+12DD 20MM 44.444SS '
    >>> angle.fmt_angle(-1, s1="DD ", s2="MM ", s3="SS ")
    '-01DD 00MM 00.000SS '
    >>> angle.fmt_angle(-1, s1="DD ", s2="MM ", s3="SS ", lower=0, upper=360)
    '+359DD 00MM 00.000SS '

    """
    if not lower or not upper:  # Don't normalize if range not given.
        n = val
    else:
        n = normalize(val, lower=lower, upper=upper, b=b)

    x = deci2sexa(n, pre=pre, trunc=trunc)

    p = "{3:0" + "{0}.{1}".format(pre + 3, pre) + "f}" + s3
    p = "{0}{1:02d}" + s1 + "{2:02d}" + s2 + p

    return p.format("-" if x[0] < 0 else "+", *x[1:])


def phmsdms(hmsdms):
    """Parse a string containing a sexageismal number.

    This can handle several types of delimiters and will process
    reasonably valid strings. See examples

    Parameters
    ----------
    hmsdms : str
        String containing a sexagesimal number.

    Returns
    -------
    d : dict

        parts : a 3 element list of floats
            The three parts of the sexagesimal number, identified.
        vals : 3 element list of floats
            The numerical values of the three parts of the sexagesimal
            number.
        sign : int
            Sign of the sexagesimal number; 1 for positive and -1 for
            negative.
        units : {'degrees", "hours"}
            The units of the sexagesimal number. This is infered from
            the presence of characters present in the string. If it a
            pure number then the units is degrees.

    Examples
    --------
    >>> angle.phmsdms("12")

    {'parts': [12.0, None, None],
     'sign': 1,
     'units': 'degrees',
     'vals': [12.0, 0.0, 0.0]}
    >>> angle.phmsdms("12")

    {'parts': [12.0, None, None],
     'sign': 1,
     'units': 'degrees',
     'vals': [12.0, 0.0, 0.0]}
    >>> angle.phmsdms("12d13m14.56")

    {'parts': [12.0, 13.0, 14.56],
     'sign': 1,
     'units': 'degrees',
     'vals': [12.0, 13.0, 14.56]}
    >>> angle.phmsdms("12d13m14.56ss")

    {'parts': [12.0, 13.0, 14.56],
     'sign': 1,
     'units': 'degrees',
     'vals': [12.0, 13.0, 14.56]}
    >>> angle.phmsdms("12d14.56ss")

    {'parts': [12.0, None, 14.56],
     'sign': 1,
     'units': 'degrees',
     'vals': [12.0, 0.0, 14.56]}
    >>> angle.phmsdms("14.56ss")

    {'parts': [None, None, 14.56],
     'sign': 1,
     'units': 'degrees',
     'vals': [0.0, 0.0, 14.56]}

    """
    units = None
    sign = None
    # Floating point regex:
    # http://www.regular-expressions.info/floatingpoint.html
    #
    # pattern1: find a decimal number (int or float) and any
    # characters following it upto the next decimal number.  [^0-9\-+]*
    # => keep gathering elements until we get to a digit, a - or a
    # +. These three indicates the possible start of the next number.
    pattern1 = re.compile(r"([-+]?[0-9]*\.?[0-9]+[^0-9\-+]*)")

    # pattern2: find decimal number (int or float) in string.
    pattern2 = re.compile(r"([-+]?[0-9]*\.?[0-9]+)")

    hmsdms = hmsdms.lower()
    hdlist = pattern1.findall(hmsdms)

    parts = [None, None, None]

    def _fill_right_not_none():
        # Find the right pos. where parts is not None. Next value must
        # be inserted to the right of this. If this is 2 then we have
        # already filled seconds part, raise exception. If this is 1
        # then fill 2. If this is 0 fill 1. If none of these then fill
        # 0.
        rp = reversed(parts)
        for i, j in enumerate(rp):
            if j is not None:
                break
        if  i == 0:
            # Seconds part already filled.
            raise ValueError("Invalid string.")
        elif i == 1:
            parts[2] = v
        elif i == 2:
            # Either parts[0] is None so fill it, or it is filled
            # and hence fill parts[1].
            if parts[0] is None:
                parts[0] = v
            else:
                parts[1] = v

    for valun in hdlist:
        try:
            # See if this is pure number.
            v = float(valun)
            # Sexagesimal part cannot be determined. So guess it by
            # seeing which all parts have already been identified.
            _fill_right_not_none()
        except ValueError:
            # Not a pure number. Infer sexagesimal part from the
            # suffix.
            if "hh" in valun or "h" in valun:
                m = pattern2.search(valun)
                parts[0] = float(valun[m.start():m.end()])
                units = "hours"
            if "dd" in valun or "d" in valun:
                m = pattern2.search(valun)
                parts[0] = float(valun[m.start():m.end()])
                units = "degrees"
            if "mm" in valun or "m" in valun:
                m = pattern2.search(valun)
                parts[1] = float(valun[m.start():m.end()])
            if "ss" in valun or "s" in valun:
                m = pattern2.search(valun)
                parts[2] = float(valun[m.start():m.end()])
            if "'" in valun:
                m = pattern2.search(valun)
                parts[1] = float(valun[m.start():m.end()])
            if '"' in valun:
                m = pattern2.search(valun)
                parts[2] = float(valun[m.start():m.end()])
            if ":" in valun:
                # Sexagesimal part cannot be determined. So guess it by
                # seeing which all parts have already been identified.
                v = valun.replace(":", "")
                v = float(v)
                _fill_right_not_none()
        if not units:
            units = "degrees"

    # Find sign. Only the first identified part can have a -ve sign.
    for i in parts:
        if i and i < 0.0:
            if sign is None:
                sign = -1
            else:
                raise ValueError("Only one number can be negative.")

    if sign is None:  # None of these are negative.
        sign = 1

    vals = [abs(i) if i is not None else 0.0 for i in parts]

    return dict(sign=sign, units=units, vals=vals, parts=parts)


class Angle(object):
    """A class for representing angles, including string formatting.

    This is the basic Angle object. The value of the angle is
    initialized to the given value. Default is 0 radians. This class
    will accept any reasonably well formatted sexagesimal string
    representation, instead of a numerical value for angles.

    Parameters
    ----------
    r : float
        Angle in radians.
    d : degrees
        Angle in degrees.
    h : float
        Angle in hours.
    mm : float
        The second part, i.e., minutes, of a sexagesimal number.
    ss : float
        The third part, i.e., seconds, of a sexagesimal number.
    sg : str
        A string containing a sexagesimal number.

    Atttributes
    -----------
    r
    d
    h
    arcs
    ounit
    pre : float
        Number of decimal digits to include in the last part of the
        sexagesimal string representation of this angle. This is
        generated when the angle is converted into a string.
    trunc : bool
        If True, then the third part of the sexagesimal representation
        is truncated to `pre` places, else it is rounded. Default is
        False.
    s1 : str
        Separator between first and second parts of sexagesimal string.
    s2 : str
        Separator between second and third parts of sexagesimal string.
    s1 : str
        Separator after the third part of sexagesimal string.

    Notes
    -----
    The output string representation depends on `ounit`, `pre` and
    `trunc` attributes. The first one determines the unit. It can be
    "radians", "degrees" or "hours". For "radians", the string
    representation is just the number itself. Attribute `pre`
    determines the number of decimal places in the last part of the
    sexagesimal representation. This can be negative. If `trunc` is
    true then the number is truncated to `pre` places, else it is
    rounded. The latter is the default.

    See also
    --------
    phmsdms
    sexa2deci
    deci2sexa
    normalize

    Examples
    --------
    >>> import angle
    >>> a = angle.Angle(sg="12h34m16.592849219")
    >>> print a.r, a.d, a.h, a.arcs
    3.29115230606 188.569136872 12.5712757914 678848.892738
    >>> print a.ounit
    hours
    >>> print a
    +12 34 16.593
    >>> print a.pre, a.trunc
    3 False
    >>> a.pre = 4
    >>> print a
    +12 34 16.5928
    >>> a.pre = 3
    >>> a.trunc = True
    >>> print a
    +12 34 16.592
    >>> a.ounit = "degrees"
    >>> print a
    +188 34 08.8927
    >>> a.ounit = "radians"
    >>> print a
    3.29115230606
    >>> a.ounit = "degrees"
    >>> a.s1 = "DD "
    >>> a.s2 = "MM "
    >>> a.s3 = "SS "
    >>> print a
    +188DD 34MM 08.8927SS
    >>> a.s1 = u"\u00B0 "
    >>> print unicode(a)
    +12° 34MM 16.593SS

    But this will cause problems when converting to string in Python 2.x:
    that is a `print a` will raise UnicodeEncodeError.

    Angle objects and be added to and subtracted from each other.

    >>> a = angle.Angle(h=12.5)
    >>> b = angle.Angle(h=13.0)
    >>> c = a - b
    >>> c.h
    -0.5000000000000011
    >>> c = a + b
    >>> c.h
    25.5

    """
    __units = ("radians", "degrees", "hours")
    __keyws = ('r', 'd', 'h', 'mm', 'ss', "sg")
    __raw = 0.0
    __iunit = 0
    __ounit = "radians"
    pre = 3
    trunc = False
    s1 = " "
    s2 = " "
    s3 = " "

    def __init__(self, sg=None, **kwargs):
        if sg != None:
            # Insert this into kwargs so that the conditional below
            # gets it.
            kwargs['sg'] = str(sg)
        x = (True if i in self.__keyws else False for i in kwargs)
        if not all(x):
            raise TypeError("Only {0} are allowed.".format(self.__keyws))
        if "sg" in kwargs:
            x = phmsdms(kwargs['sg'])
            if x['units'] not in self.__units:
                raise ValueError("Unknow units: {0}".format(x['units']))
            self.__iunit = self.__units.index(x['units'])
            if self.__iunit == 1:
                self.__raw = d2r(sexa2deci(x['sign'], *x['vals']))
            elif self.__iunit == 2:
                self.__raw = h2r(sexa2deci(x['sign'], *x['vals']))
            if len(kwargs) != 1:
                warnings.warn("Only sg = {0} used.".format(kwargs['sg']))
        elif "r" in kwargs:
            self.__iunit = 0
            self.__raw = kwargs['r']
            if len(kwargs) != 1:
                warnings.warn("Only r = {0} used.".format(kwargs['r']))
        else:
            if "d" in kwargs:
                self.__iunit = 1
                self.__raw = d2r(sexa2deci(1, kwargs['d'],
                                      kwargs.get('mm', 0.0),
                                      kwargs.get('ss', 0.0)))
                if "h" in kwargs:
                    warnings.warn("h not used.")
            elif "h" in kwargs:
                self.__iunit = 2
                self.__raw = h2r(sexa2deci(1, kwargs['h'],
                                      kwargs.get('mm', 0.0),
                                      kwargs.get('ss', 0.0)))

        self.__ounit = self.__units[self.__iunit]

    def __getr(self):
        return self.__raw

    def __setr(self, val):
        self.__raw = float(val)

    r = property(__getr, __setr, doc="Angle in radians.")

    def __getd(self):
        return r2d(self.__raw)

    def __setd(self, val):
        self.__raw = d2r(float(val))

    d = property(__getd, __setd, doc="Angle in degrees.")

    def __geth(self):
        return r2h(self.__raw)

    def __seth(self, val):
        self.__raw = h2r(float(val))

    h = property(__geth, __seth, doc="Angle in hours.")

    def __getarcs(self):
        return r2arcs(self.__raw)

    def __setarcs(self, val):
        self.__raw = arcs2r(float(val))

    arcs = property(__getarcs, __setarcs, doc="Angle in arcseconds.")

    def __getounit(self):
        return self.__ounit

    def __setounit(self, val):
        if val not in self.__units:
            raise ValueError("Unit can only be {0}".format(self.__units))
        self.__ounit = val

    ounit = property(__getounit, __setounit, doc="String output unit.")

    def __repr__(self):
        return str(self.r)

    def __str__(self):
        if self.ounit == "radians":
            return str(self.r)
        elif self.ounit == "degrees":
            return fmt_angle(self.d, s1=self.s1, s2=self.s2,
                             s3=self.s3,
                             pre=self.pre, trunc=self.trunc)
        elif self.ounit == "hours":
            return fmt_angle(self.h, s1=self.s1, s2=self.s2,
                             s3=self.s3,
                             pre=self.pre, trunc=self.trunc)

    def __add__(self, other):
        if not isinstance(other, Angle):
            raise ValueError("Addition needs to Angle objects.")
        return Angle(r=self.r + other.r)

    def __sub__(self, other):
        if not isinstance(other, Angle):
            raise ValueError("Subtraction needs two Angle objects.")
        return Angle(r=self.r - other.r)


class AlphaAngle(Angle):
    """Angle for longitudinal angles such as Right Ascension.

    AlphaAngle is a subclass of Angle that can be used to represent
    longitudinal angles such as Right Ascension, azimuth and longitude.

    In AlphaAngle the attribute `ounit` is always "hours", repr()
    always gives angle in hours and formatting is always as an HMS
    sexagesimal string.

    The angle is normalized to [0, 24) hours.

    This takes the same parameters as the `Angle` class, and has the
    same attributes as the `Angle` class. The attribute `ounit` is
    read-only. The additonal attributes are given below.

    Attributes
    ----------
    norm : float
        Angle normalized to [0, 24.0) hours.
    hms : tuple (int, int, int, float)
        Sexagesimal, HMS, parts of the angle as tuple: first item is
        sign, second is hours, third is minutes and the fourth is
        seconds. Sign is 1 for positive and -1 for negative.
    sign : int
        Sign of the angle. 1 for positive and -1 for negative. Sign
        applies to the whole angle and not to any single part.
    hh : int
        The hours part of sexagesimal number, between [0,23]
    mm : int
        The minutes part of sexagesimal number, between [0, 59]
    ss : float
        The seconds part of sexagesimal number.

    Notes
    -----
    The `pre` and `trunc` properties will affect both the string
    representation as well as the sexagesimal parts. The angle is
    normalized into [0, 24) hours in such a way that 25 hours become 1
    hours and -1 hours become 23 hours.

    See also
    --------
    Angle (for other attributes)

    Examples
    --------
    >>> import angle
    >>> a = angle.AlphaAngle(d=180.5)
    >>> print a
    +12HH 02MM 00.000SS
    >>> a = angle.AlphaAngle(h=12.0)
    >>> print a
    +12HH 00MM 00.000SS
    >>> a = angle.AlphaAngle(h=-12.0)
    >>> a.norm
    12.0
    >>> a.ounit
    "hours"
    >>> print a
    +12HH 00MM 00.000SS
    >>> a.h
    -12.0

    If no keyword is provided then the input is taken to a sexagesimal
    string and the units will be determined from it.

    >>> a = angle.AlphaAngle("12h14m23.4s")
    >>> print a
    +12HH 14MM 23.400SS

    The `hms` attribute contains the sexagesimal represenation. These
    are also accessible as `a.sign`, a.hh`, `a.mm` and `a.ss`. The
    `pre` and `trunc` attributes are taken into account. Angle in
    radians, hours, degrees and arc-seconds can be extracted from
    appropriate attributes.

    >>> a.hms
    (1, 12, 0, 0.0)
    >>> a = angle.AlphaAngle(h=12.54678345)
    >>> a.hms
    (1, 12, 32, 48.42)
    >>> a.sign, a.hh, a.mm, a.ss
    (1, 12, 32, 48.42)
    >>> a.r, a.h, a.d, a.arcs
    (3.2847402260585, 12.54678345, 188.20175175, 677526.3063)
    >>> print a
    +12HH 32MM 48.420SS
    >>> a.pre = 5
    >>> a.hms
    (1, 12, 32, 48.42042)
    >>> print a
    +12HH 32MM 48.42042SS

    Separators can be changed.

    >>> a.s1 = " : "
    >>> a.s2 = " : "
    >>> a.s3 = ""
    >>> print a
    +12 : 32 : 48.420

    Angles are properly normalized.

    >>> a = angle.AlphaAngle(h=25.0)
    >>> print a
    +01HH 00MM 00.000SS
    >>> a = angle.AlphaAngle(h=-1.0)
    >>> print a
    +23HH 00MM 00.000SS

    The sexagesimal parts are properly converted into their respective
    ranges.

    >>> a.hh = 23
    >>> a.mm = 59
    >>> a.ss = 59.99999
    >>> a.hms
    (1, 24, 0, 0.0)
    >>> print a
    +24 : 00 : 00.000
    >>> a.pre = 4
    >>> print a
    +24 : 00 : 00.0000
    >>> a.hms
    (1, 24, 0, 0.0)
    >>> a.pre = 5
    >>> print a
    +23 : 59 : 59.99999
    >>> a.hms
    (1, 23, 59, 59.99999)

    Angles can be added to and subtracted from each other.

    >>> a = angle.AlphaAngle(h=12.0)
    >>> b = angle.AlphaAngle(h=13.0)
    >>> c = a - b
    >>> c.h
    -1.0000000000000007
    >>> c = a + b
    >>> c.h
    25.0

    """
    def __init__(self, sg=None, **kwargs):
        Angle.__init__(self, sg, **kwargs)
        self.__ounit = "hours"
        self.s1 = "HH "
        self.s2 = "MM "
        self.s3 = "SS"

    def __getnorm(self):
        return h2h(self.h)

    norm = property(fget=__getnorm, doc="Angle normalized to [0, 24) h.")

    def __getounit(self):
        return self.__ounit

    ounit = property(fget=__getounit,
                     doc="Formatting unit: always hours for RA.")

    def __gethms(self):
        return deci2sexa(self.norm, pre=self.pre, trunc=self.trunc)

    def __sethms(self, val):
        if len(val) != 4:
            raise ValueError(
                "HMS must be of the form [sign, HH, MM, SS.ss..]")
        if val[0] not in (-1, 1):
            raise ValueError("Sign has to be -1 or 1.")

        self.h = sexa2deci(*val)

    hms = property(__gethms, __sethms, doc="HMS tuple.")

    def __getsign(self):
        return self.hms[0]

    def __setsign(self, sign):
        if sign not in (-1, 1):
            raise ValueError("Sign has to be -1 or 1.")
        self.h *= sign

    sign = property(__getsign, __setsign, doc="Sign of HMS angle.")

    def __gethh(self):
        return self.hms[1]

    def __sethh(self, val):
        if type(val) != type(1):
            raise ValueError("HH takes only integers.")
        x = self.hms
        self.h = sexa2deci(x[0], val, x[2], x[3])

    hh = property(__gethh, __sethh, doc="HH of HMS angle.")

    def __getmm(self):
        return self.hms[2]

    def __setmm(self, val):
        if type(val) != type(1):
            raise ValueError("MM takes integers only.")
        x = self.hms
        self.h = sexa2deci(x[0], x[1], val, x[3])

    mm = property(__getmm, __setmm, doc="MM of HMS angle.")

    def __getss(self):
        return self.hms[3]

    def __setss(self, val):
        x = self.hms
        self.h = sexa2deci(x[0], x[1], x[2], val)

    ss = property(__getss, __setss, doc="SS of HMS angle.")

    def __str__(self):
        # Always HMS.
        return fmt_angle(self.h, s1=self.s1, s2=self.s2, s3=self.s3,
                         pre=self.pre, trunc=self.trunc,
                         lower=0.0, upper=24.0)

    def __add__(self, other):
        """Adds any type of angle to this."""
        if not isinstance(other, Angle):
            raise ValueError("Addition needs two Angle objects.")
        return AlphaAngle(r=self.r + other.r)

    def __sub__(self, other):
        """Subtracts any type of angle from this."""
        if not isinstance(other, Angle):
            raise ValueError("Subtraction needs two Angle objects.")
        return AlphaAngle(r=self.r - other.r)


class DeltaAngle(Angle):
    """Angle for latitudinal angles such as Declination.

    DeltaAngle is a subclass of Angle for latitudinal angles such as
    Declination, elevation and latitude.

    In DeltaAngle the attribute `ounit` is always "degrees", repr()
    always gives angle in degrees and formatting is always as a DMS
    sexagesimal string.

    The angle is normalized to the range [-90, 90] degrees.

    This takes the same parameters as the `Angle` class, and has the
    same attributes as the `Angle` class. The attribute `ounit` is
    read-only. The additonal attributes are given below.

    Attributes
    ----------
    norm : float
        Angle normalized to [-90, 90] degrees.
    dms : tuple (int, int, int, float)
        Sexagesimal, DMS, parts of the angle as tuple: first item is
        sign, second is degrees, third is arc-minutes and the fourth is
        arc-seconds. Sign is 1 for positive and -1 for negative.
    sign : int
        Sign of the angle. 1 for positive and -1 for negative. Sign
        applies to the whole angle and not to any single part.
    dd : int
        The degrees part of sexagesimal number, between [-90, 90]
    mm : int
        The arc-minutes part of sexagesimal number, between [0, 59]
    ss : float
        The arc-seconds part of sexagesimal number.

    Notes
    -----
    The `pre` and `trunc` properties will affect both the string
    representation as well as the sexagesimal parts. The angle is
    normalized between [-90, 90], in such a way that -91 becomes -89
    and 91 becomes 89.

    See also
    --------
    Angle (for other attributes)

    Examples
    --------
    >>> import angle
    >>> a = angle.DeltaAngle(sg="-12dd13.5mm18.9459823198")
    >>> a.norm
    -12.230262772866611
    >>> a = angle.DeltaAngle(d=-98)
    >>> a.norm
    -82.0
    >>> a.ounit
    'degrees'
    >>> print a
    -12DD 13MM 48.94598SS
    >>> a = angle.DeltaAngle(d=180.0)
    >>> print a
    +00DD 00MM 00.000SS
    >>> a = angle.DeltaAngle(h=12.0)
    >>> print a
    +00DD 00MM 00.000SS

    If no keyword is provided then the input is taken to a sexagesimal
    string and the units will be determined from it.

    >>> a = angle.DeltaAngle("12d23m14.2s")
    >>> print a
    +12DD 23MM 14.200SS

    The `dms` attribute contains the sexagesimal represenation. These
    are also accessible as `a.sign`, a.dd`, `a.mm` and `a.ss`. The
    `pre` and `trunc` attributes are taken into account. Angle in
    radians, hours, degrees and arc-seconds can be extracted from
    appropriate attributes.

    >>> a = angle.DeltaAngle(d=12.1987546)
    >>> a.dms
    (1, 12, 11, 55.517)
    >>> a.pre = 5
    >>> a.dms
    (1, 12, 11, 55.51656)
    >>> a.sign, a.dd, a.mm, a.ss
    (1, 12, 11, 55.51656)
    >>> a.r, a.d, a.h, a.arcs
    (0.21290843241280386, 12.1987546, 0.8132503066666666, 43915.51656)

    The separators can be changed.

    >>> a = angle.DeltaAngle(d=12.3459876)
    >>> a.s1 = " : "
    >>> a.s2 = " : "
    >>> a.s3 = ""
    >>> print a
    +12 : 20 : 45.555

    Angles are properly normalized.

    >>> a = angle.DeltaAngle(d=-91.0)
    >>> print a
    -89DD 00MM 00.000SS
    >>> a = angle.DeltaAngle(d=91.0)
    >>> print a
    +89DD 00MM 00.000SS

    The sexagesimal parts are properly normalized into their respective
    ranges.

    >>> a.dd = 89
    >>> a.mm = 59
    >>> a.ss = 59.9999
    >>> print a
    +90DD 00MM 00.000SS
    >>> a.pre = 5
    >>> print a
    +89DD 59MM 59.99990SS
    >>> a.dd = 89
    >>> a.mm = 60
    >>> a.ss = 60
    >>> print a
    +89DD 59MM 00.000SS

    Angles can be added to and subtracted from each other.

    >>> a = angle.DeltaAngle(d=12.0)
    >>> b = angle.DeltaAngle(d=13.0)
    >>> c = a - b
    >>> c.d
    -0.9999999999999998
    >>> c = a + b
    >>> c.d
    25.000000000000004
    >>> print c
    +25DD 00MM 00.000SS
    >>> c = a - b
    >>> print c
    -01DD 00MM 00.000SS

"""
    def __init__(self, sg=None, **kwargs):
        Angle.__init__(self, sg, **kwargs)
        self.__ounit = "degrees"
        self.s1 = "DD "
        self.s2 = "MM "
        self.s3 = "SS"

    def __getnorm(self):
        return normalize(self.d, lower=-90, upper=90, b=True)

    norm = property(fget=__getnorm, doc="Angle normalized to [0, 24) h.")

    def __getounit(self):
        return self.__ounit

    ounit = property(fget=__getounit,
                     doc="Formatting unit: always degrees for Dec.")

    def __repr__(self):
        return str(self.d)

    def __getdms(self):
        return deci2sexa(self.norm, pre=self.pre, trunc=self.trunc)

    def __setdms(self, val):
        if len(val) != 4:
            raise ValueError(
                "DMS must be of the form [sign, DD, MM, SS.ss..]")
        if val[0] not in (-1, 1):
            raise ValueError("Sign has to be -1 or 1.")

        self.d = sexa2deci(*val)

    dms = property(__getdms, doc="DMS tuple.")

    def __getsign(self):
        return self.dms[0]

    def __setsign(self, sign):
        if sign not in (-1, 1):
            raise ValueError("Sign has to be -1 or 1")
        self.d *= sign

    sign = property(__getsign, __setsign, doc="Sign of DMS angle.")

    def __getdd(self):
        return self.dms[1]

    def __setdd(self, val):
        if type(val) != type(1):
            raise ValueError("DD takes only integers.")
        x = self.dms
        self.d = sexa2deci(x[0], val, x[2], x[3])

    dd = property(__getdd, __setdd, doc="DD of DMS angle.")

    def __getmm(self):
        return self.dms[2]

    def __setmm(self, val):
        if type(val) != type(1):
            raise ValueError("MM takes only integers.")
        x = self.dms
        self.d = sexa2deci(x[0], x[1], val, x[3])

    mm = property(__getmm, __setmm, doc="MM of DMS angle.")

    def __getss(self):
        return self.dms[3]

    def __setss(self, val):
        x = self.dms
        self.d = sexa2deci(x[0], x[1], x[2], val)

    ss = property(__getss, __setss, doc="SS of DMS angle.")

    def __unicode__(self):
        # Always DMS.
        return fmt_angle(self.d, s1=self.s1, s2=self.s2, s3=self.s3,
                         pre=self.pre, trunc=self.trunc,
                         lower=-90, upper=90, b=True)

    def __str__(self):
        # Always DMS.
        return fmt_angle(self.d, s1=self.s1, s2=self.s2, s3=self.s3,
                         pre=self.pre, trunc=self.trunc,
                         lower=-90, upper=90, b=True)

    def __add__(self, other):
        """Adds any type of angle to this."""
        if not isinstance(other, Angle):
            raise ValueError("Addition needs two Angle objects.")
        return DeltaAngle(r=self.r + other.r)

    def __sub__(self, other):
        """Subtracts any type of angle from this."""
        if not isinstance(other, Angle):
            raise ValueError("Subtraction needs two Angle objects.")
        return DeltaAngle(r=self.r - other.r)


class CartesianVector(object):
    """A 3D Cartesian vector."""
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = x
        self.y = y
        self.z = z

    def dot(self, v):
        return self.x * v.x + self.y * v.y + self.z * v.z

    def cross(self, v):
        n = self.__class__()
        n.x = self.y * v.z - self.z * v.y
        n.y = - (self.x * v.z - self.z * v.x)
        n.z = self.x * v.y - self.y * v.x

        return n

    @property
    def mod(self):
        """Modulus of vector."""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def from_s(self, r=1.0, alpha=0.0, delta=0.0):
        """Construct Cartesian vector from spherical coordinates.

        alpha and delta must be in radians.
        """
        self.x = r * math.cos(delta) * math.cos(alpha)
        self.y = r * math.cos(delta) * math.sin(alpha)
        self.z = r * math.sin(delta)

    def __repr__(self):
        return str(self.x, self.y, self.z)

    def __str__(self):
        self.___repr__()


class AngularPosition(object):
    """Class for storing a point on a unit sphere, say (RA, DEC).

    AngularPosition can be used to work with points on a sphere. This
    object stores two attributes `alpha` and `delta` that represent the
    longitudinal and latitudinal angles, repectively. The former is of
    type `AlphaAngle` and the latter is of type `DeltaAngle`.

    The string representation of AngularPosition is constructed using
    both alpha and delta.

    Difference between two AngularPosition gives the separation between
    them, in radians.

    The separation between two angular positions can also be obtained
    by calling the method `sep`.

    The bearing between two points can be obtained using the `bear`
    method.

    Parameters
    ----------
    alpha : float, str
        The longitudinal angle. If value is afloat then it is taken to
        be the angle in hours. If value is str then it is treated as a
        sexagesimal number and the units are determined from
        it. Default is 0.0.

    delta : float, str
        The latitudinal angle. If value is float then it is taken to be
        the angle in degrees. If value is str then it is treated as a
        sexagesimal number and the units are determined from
        it. Default is 0.0.

    Attributes
    ----------
    dlim : str
        Delimiter to use between alpha and delta angles in string
        representation.

    Methods
    -------
    sep : return great circle separation in radians.
    bear : return position angle in radians.

    See also
    --------
    Angle
    AlphaAngle
    DeltaAngle

    Examples
    --------
    >>> pos1 = angle.AngularPosition(alpha=12.0, delta=90.0)
    >>> pos2 = angle.AngularPosition(alpha=12.0, delta=0.0)
    >>> angle.r2d(pos1.sep(pos2))
    90.0
    >>> angle.r2d(pos2.sep(pos1))
    90.0
    >>> angle.r2d(pos1 - pos2)
    90.0
    >>> angle.r2d(pos2 - pos1)
    90.0

    """
    # Separator between alpha and delta when returning string
    # representation.
    dlim = " "

    def __init__(self, alpha=0.0, delta=0.0):
        if type(alpha) == type(" "):
            self.__alpha = AlphaAngle(sg=alpha)
        else:
            self.__alpha = AlphaAngle(h=alpha)
        if type(delta) == type(" "):
            self.__delta = DeltaAngle(sg=delta)
        else:
            self.__delta = DeltaAngle(d=delta)

    def __getalpha(self):
        return self.__alpha

    def __setalpha(self, a):
        if not isinstance(a, AlphaAngle):
            raise TypeError("alpha must be of type AlphaAngle.")
        else:
            self.__alpha = a

    alpha = property(fget=__getalpha, fset=__setalpha,
                     doc="Longitudinal angle (AlphaAngle).")

    def __getdelta(self):
        return self.__delta

    def __setdelta(self, a):
        if not isinstance(a, DeltaAngle):
            raise TypeError("delta must be of type DeltaAngle.")
        else:
            self.__delta = a

    delta = property(fget=__getdelta, fset=__setdelta,
                     doc="Latitudinal angle (DeltaAngle).")

    def sep(self, p):
        """Angular spearation between objects in radians.

        This will be an angle between [0, π].

        Parameters
        ----------
        p : AngularPosition
            The object to which the separation from the current object
            is to be calculated.

        Notes
        -----
        Results agree with those from SLALIB rountine sla_dsep.

        """
        v = CartesianVector()
        v.from_s(1.0, self.alpha.r, self.delta.r)
        v2 = CartesianVector()
        v2.from_s(1.0, p.alpha.r, p.delta.r)
        d = v.dot(v2)
        c = v.cross(v2).mod
        tol = 1e-8
        if abs(d) < tol or not abs(c) < tol:
            return 0.0
        else:
            res = math.atan2(c, d)
            if abs(res) < tol:
                return 0.0
            else:
                return res

    def bear(self, p):
        """Find position angle between objects, in radians.

        Position angle of the given object with respect to this object
        is returned in degrees. Position angle is calculated clockwise
        and counter-clockwise from the direction towards the North
        pole. It is between (0 and π) if the given object is in the
        eastern hemisphere w.r.t this object, and between (0, -π) if
        the object is in the western hemisphere w.r.t this object.

        Parameters
        ----------
        p : AngularPosition
            The object to which bearing must be determined.

        Notes
        -----
        Results agree with those from SLALIB rountine sla_dbear. If the
        first point, i.e. this object, is at the pole then bearing is
        undefined and 0 is returned.

        """
        # Find perpendicular to the plane containing the base and
        # z-axis. Then find the perpendicular to the plane containing
        # the base and the target. The angle between these two is the
        # position angle or bearing of the target w.r.t the base. Check
        # sign of the z component of the latter vector to determine
        # quadrant: 1st and 2nd quadrants are +ve while 3rd and 4th are
        # negative.
        v1 = CartesianVector()
        v1.from_s(1.0, self.alpha.r, self.delta.r)
        v2 = CartesianVector()
        v2.from_s(1.0, p.alpha.r, p.delta.r)

        # Z-axis
        v0 = CartesianVector()
        v0.from_s(r=1.0, alpha=0.0, delta=d2r(90.0))

        # Vector perpendicular to great circle containing two points.
        v12 = v1.cross(v2)

        # Vector perpendicular to great circle containing base and
        # Z-axis.
        v10 = v1.cross(v0)

        # Find angle between these two vectors.
        dot = v12.dot(v10)
        cross = v12.cross(v10).mod
        x = math.atan2(cross, dot)

        # If z is negative then we are in the 3rd or 4th quadrant.
        if v12.z < 0.0:
            x = -x
        tol = 1e-8
        if abs(x) < tol:
            return 0
        else:
            return x

    def __str__(self):
        return self.dlim.join([self.alpha.__str__(),
                               self.delta.__str__()])

    def __repr__(self):
        # Return alpha in hours and delta in degrees. Should be able to
        # **eval(d) this to constructor and recreate this position.
        return str(dict(alpha=self.alpha.h, delta=self.delta.d))

    def __sub__(self, other):
        if type(other) != type(self):
            raise TypeError("Subtraction needs an AngularPosition object.")
        return self.sep(other)


# Test for AngularPosition.sep() with SLALIB sla_dsep.
#
# >>> from pyslalib import slalib
# >>> alpha = [random.uniform(0,math.pi) for i in range(100)]
# >>> alpha = [random.uniform(0,2*math.pi) for i in range(100)]
# >>> delta = [random.uniform(-math.pi/2, math.pi/2) for i in range(100)]
# >>> alpha1 = [random.uniform(0,2*math.pi) for i in range(100)]
# >>> delta1 = [random.uniform(-math.pi/2, math.pi/2) for i in range(100)]
#
# >>> s = [slalib.sla_dsep(alpha[i], delta[i], alpha1[i], delta1[i])
#   ....: for i in range(100)]
# >>> from angle import AngularPosition
# >>> pos1 = [AngularPosition() for i in range(100)]
# >>> for i in range(100):
#    ....:     pos1[i].alpha.r = alpha[i]
#    ....:     pos1[i].delta.r = delta[i]
#    ....:
#    ....:
# >>> for i in range(100):
#     pos2[i].alpha.r = alpha1[i]
#     pos2[i].delta.r = delta1[i]
#    ....:
#    ....:
# >>> s1 = [pos1[i].sep(pos2[i]) for i in range(100)]
# >>> d = [i-j for i, j in zip(s, s1)]
# >>> min(d)
# -4.4408920985006262e-16
# >>> max(d)
# 2.2204460492503131e-16
#
# Test AngularPosition.bear() with SLALIB sla_dbear.
#
# >>> s = [slalib.sla_dbear(alpha[i], delta[i], alpha1[i], delta1[i])
# for i in range(100)]
# >>> s1 = [pos1[i].bear(pos2[i]) for i in range(100)]
# >>> d = [i-j for i, j in zip(s, s1)]
# >>> min(d)
# -1.1102230246251565e-15
# >>> max(d)
# 8.8817841970012523e-16
