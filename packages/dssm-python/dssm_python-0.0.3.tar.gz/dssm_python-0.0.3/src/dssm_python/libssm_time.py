import ctypes
import time
from typing import Optional

import sysv_ipc


SHM_KEY = 0x3292
SHM_TIME_KEY = SHM_KEY - 1


class SSMTimeT(ctypes.Structure):
    _fields_ = [
        ("time", ctypes.c_double),
    ]

    def __repr__(self):
        return f"SSMTimeT(time={self.time})"


class SSMTime(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("offset", SSMTimeT),
        ("speed", ctypes.c_double),
        ("is_pause", ctypes.c_int),
        ("pausetime", SSMTimeT),
    ]

    def __repr__(self):
        return (f"SSMTime(offset={self.offset}, speed={self.speed}, is_pause={self.is_pause}, "
                f"pausetime={self.pausetime})")


shm_time: Optional[sysv_ipc.SharedMemory] = None
timecontrol: Optional[SSMTime] = None


def get_time_ssm() -> SSMTimeT:
    global timecontrol
    if timecontrol is not None:
        if timecontrol.is_pause:
            return timecontrol.pausetime
        return SSMTimeT(timecontrol.speed * get_time_ssm_real().time + timecontrol.offset.time)
    return get_time_ssm_real()


def get_time_ssm_real() -> SSMTimeT:
    current = time.time()
    return SSMTimeT(current)


def timetof(t: time.struct_time) -> float:
    return t.tv_sec + t.tv_nsec / 1000000000.0


def nanosleep_ssm(req: float):
    global timecontrol
    if timecontrol is not None and timecontrol.speed != 0.0:
        speed = abs(timecontrol.speed)
        adjusted_time = req / speed
        time.sleep(adjusted_time)
    else:
        time.sleep(req)


def sleep_ssm(sec: float):
    return nanosleep_ssm(sec)


def usleep_ssm(usec: int):
    return nanosleep_ssm(usec / 1000000.0)


# --------------------------------------------------------


# Get SSM speed
def get_time_ssm_speed() -> float:
    global timecontrol
    if timecontrol is not None:
        return timecontrol.speed
    return 1.0


# Get SSM pause status
def get_time_ssm_is_pause() -> int:
    global timecontrol
    if timecontrol is not None:
        return timecontrol.is_pause
    return 0


# Get SSM reverse status
def get_time_ssm_is_reverse() -> int:
    if get_time_ssm_speed() < 0.0:
        return 1
    return 0


# --------------------------------------------------------


def set_time_ssm(ssm_time: SSMTimeT) -> int:
    global timecontrol
    if timecontrol is not None:
        timecontrol.offset = SSMTimeT(ssm_time.time - timecontrol.speed * get_time_ssm_real().time)
        timecontrol.pausetime = ssm_time
        return 1
    return 0


def set_speed_ssm(speed: float):
    global timecontrol
    if timecontrol is not None:
        ssm_time = get_time_ssm()
        timecontrol.speed = speed
        set_time_ssm(ssm_time)
        return 1
    return 0


def set_time_ssm_is_pause(is_pause: int) -> int:
    global timecontrol
    if timecontrol is not None:
        ssm_time = get_time_ssm()
        timecontrol.pausetime = ssm_time
        set_time_ssm(ssm_time)
        timecontrol.is_pause = is_pause
        return 1
    return 0


# --------------------------------------------------------


def init_time_ssm():
    global timecontrol
    if timecontrol is not None:
        timecontrol.offset = SSMTimeT(0.0)
        timecontrol.speed = 1.0
        timecontrol.is_pause = 0


def open_time_ssm() -> int:
    global timecontrol, shm_time
    try:
        shm_time = sysv_ipc.SharedMemory(SHM_TIME_KEY)
        memory = shm_time.read()
        timecontrol = SSMTime.from_buffer_copy(memory)

        return 1
    except sysv_ipc.ExistentialError as e:
        print(f"libssm-time : opentimeSSM : {str(e)}")
        return 0


def close_time_ssm() -> None:
    global timecontrol, shm_time
    if timecontrol is not None:
        timecontrol = None

    if shm_time is not None:
        shm_time.detach()
        shm_time = None
