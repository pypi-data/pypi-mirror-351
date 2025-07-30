import ctypes


class IniSsm(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("num", ctypes.c_int),
    ]

    def __repr__(self):
        return f"IniSsm(num={self.num})"
