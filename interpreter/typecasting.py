#LOLCODE Interpreter — Typecasting logic

from .values import (
    LolValue, NOOB_VALUE,
    TYPE_NOOB, TYPE_NUMBR, TYPE_NUMBAR, TYPE_YARN, TYPE_TROOF,
)
from .signals import RuntimeError_


def _is_numeric_yarn(s: str) -> bool:
    #True if the YARN can be cast to a number (digits, optional leading
    #hyphen, optional period)."""
    s = s.strip()
    if not s:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def typecast(val: LolValue, to_type: str, explicit: bool = False) -> LolValue:
    """
    Cast val to to_type.
    explicit=True  → MAEK / IS NOW A  (more permissive for NOOB)
    explicit=False → implicit cast inside an operation
    Raises RuntimeError_ on illegal cast.
    """
    if val.type == to_type:
        return val

    #NOOB
    if val.type == TYPE_NOOB:
        if to_type == TYPE_TROOF:
            return LolValue(False, TYPE_TROOF)   #NOOB → TROOF is always FAIL
        if explicit:
            if to_type == TYPE_NUMBR:
                return LolValue(0, TYPE_NUMBR)
            if to_type == TYPE_NUMBAR:
                return LolValue(0.0, TYPE_NUMBAR)
            if to_type == TYPE_YARN:
                return LolValue('NOOB', TYPE_YARN)
            if to_type == TYPE_NOOB:
                return NOOB_VALUE
        raise RuntimeError_(f'Cannot implicitly cast NOOB to {to_type}')

    #TROOF
    if val.type == TYPE_TROOF:
        win = val.value  #True / False
        if to_type == TYPE_NUMBR:
            return LolValue(1 if win else 0, TYPE_NUMBR)
        if to_type == TYPE_NUMBAR:
            return LolValue(1.0 if win else 0.0, TYPE_NUMBAR)
        if to_type == TYPE_YARN:
            return LolValue('WIN' if win else 'FAIL', TYPE_YARN)
        if to_type == TYPE_NOOB:
            return NOOB_VALUE

    #NUMBR
    if val.type == TYPE_NUMBR:
        n = val.value
        if to_type == TYPE_NUMBAR:
            return LolValue(float(n), TYPE_NUMBAR)
        if to_type == TYPE_YARN:
            return LolValue(str(n), TYPE_YARN)
        if to_type == TYPE_TROOF:
            return LolValue(n != 0, TYPE_TROOF)
        if to_type == TYPE_NOOB:
            return NOOB_VALUE

    #NUMBAR
    if val.type == TYPE_NUMBAR:
        f = val.value
        if to_type == TYPE_NUMBR:
            return LolValue(int(f), TYPE_NUMBR)   #truncate
        if to_type == TYPE_YARN:
            return LolValue(f'{f:.2f}', TYPE_YARN)
        if to_type == TYPE_TROOF:
            return LolValue(f != 0.0, TYPE_TROOF)
        if to_type == TYPE_NOOB:
            return NOOB_VALUE

    #YARN
    if val.type == TYPE_YARN:
        s = val.value
        if to_type == TYPE_NUMBR:
            if _is_numeric_yarn(s):
                return LolValue(int(float(s.strip())), TYPE_NUMBR)
            raise RuntimeError_(f'Cannot cast YARN "{s}" to NUMBR')
        if to_type == TYPE_NUMBAR:
            if _is_numeric_yarn(s):
                return LolValue(float(s.strip()), TYPE_NUMBAR)
            raise RuntimeError_(f'Cannot cast YARN "{s}" to NUMBAR')
        if to_type == TYPE_TROOF:
            return LolValue(s != '', TYPE_TROOF)
        if to_type == TYPE_NOOB:
            return NOOB_VALUE

    raise RuntimeError_(f'Cannot cast {val.type} to {to_type}')


def to_yarn(val: LolValue) -> str:
    #Convert any LolValue to its YARN string representation.
    v = typecast(val, TYPE_YARN, explicit=True)
    return v.value


def to_troof(val: LolValue) -> bool:
    """Convert any LolValue to Python bool via TROOF cast."""
    v = typecast(val, TYPE_TROOF, explicit=False)
    return v.value


def coerce_arithmetic(a: LolValue, b: LolValue):
    """
    Coerce two values to numeric types for arithmetic.
    Returns (a', b', result_type).
    result_type is NUMBAR if either operand is NUMBAR, else NUMBR.
    """
    if a.type not in (TYPE_NUMBR, TYPE_NUMBAR):
        a = typecast(a, TYPE_NUMBAR if '.' in str(a.value) else TYPE_NUMBR)
    if b.type not in (TYPE_NUMBR, TYPE_NUMBAR):
        b = typecast(b, TYPE_NUMBAR if '.' in str(b.value) else TYPE_NUMBR)

    if a.type == TYPE_NUMBAR or b.type == TYPE_NUMBAR:
        result_type = TYPE_NUMBAR
        a = typecast(a, TYPE_NUMBAR)
        b = typecast(b, TYPE_NUMBAR)
    else:
        result_type = TYPE_NUMBR

    return a, b, result_type