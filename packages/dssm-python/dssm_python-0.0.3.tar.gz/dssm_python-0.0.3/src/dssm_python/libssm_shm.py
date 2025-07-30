import ctypes
from typing import Optional

import sysv_ipc


class SSMHeader(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("tid_top", ctypes.c_int),
        ("num", ctypes.c_int),
        ("size", ctypes.c_size_t),
        ("cycle", ctypes.c_double),
        ("data_off", ctypes.c_int),
        ("times_off", ctypes.c_int),
        ("sem_lock_id", ctypes.c_int),
        ("sem_cond_id", ctypes.c_int),
        ("sem_lock_key", ctypes.c_int),
        ("sem_cond_key", ctypes.c_int),
    ]

    def __repr__(self):
        return (f"SSMHeader(tid_top={self.tid_top}, num={self.num}, size={self.size}, cycle={self.cycle}, "
                f"data_off={self.data_off}, times_off={self.times_off}, sem_lock_id={self.sem_lock_id}, "
                f"sem_cond_id={self.sem_cond_id})")


def shm_release_ssm(shm: sysv_ipc.SharedMemory) -> int:
    try:
        shm.detach()
        return 1
    except sysv_ipc.Error:
        return 0


def shm_open_ssm(shm_id: int) -> Optional[sysv_ipc.SharedMemory]:
    try:
        shm = sysv_ipc.attach(shm_id)
        return shm
    except sysv_ipc.ExistentialError:
        return None


def shm_close_ssm(shm: sysv_ipc.SharedMemory) -> int:
    try:
        shm.detach()
        return 1
    except sysv_ipc.Error:
        return 0


def sem_release_ssm(sem: sysv_ipc.Semaphore) -> int:
    try:
        sem.release()
        return 1
    except sysv_ipc.Error:
        return 0


def sem_open_ssm(sem_key: int) -> Optional[sysv_ipc.Semaphore]:
    try:
        sem = sysv_ipc.Semaphore(sem_key)
        return sem
    except sysv_ipc.ExistentialError:
        return None
