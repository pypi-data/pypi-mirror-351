import os
import sys

from enum import Enum
from typing import Union, Tuple

from dssm_python.libssm_time import *
from dssm_python.libssm_shm import *

import sysv_ipc

MSQ_KEY = 0x3292

# MessageCommand type
MSQ_CMD = 1000
MSQ_RES = 1001
MSQ_RES_MAX = 2000

SSM_MARGIN = 1
SSM_BUFFER_MARGIN = 1.2
SSM_TID_SP = 0

SSM_SNAME_MAX = 32

msq: Optional[sysv_ipc.MessageQueue] = None
my_pid = -1


class IPC:
    def __init__(self, shm: sysv_ipc.SharedMemory = None, sem_lock: sysv_ipc.Semaphore = None,
                 sem_cond: sysv_ipc.Semaphore = None):
        self.shm = shm
        self.sem_lock = sem_lock
        self.sem_cond = sem_cond

    def __repr__(self):
        return f"IPC(SharedMemory({self.shm}), SemaphoreLock({self.sem_lock}), SemaphoreCond({self.sem_cond}))"

    def is_open(self) -> bool:
        return (isinstance(self.shm, sysv_ipc.SharedMemory) and isinstance(self.sem_lock, sysv_ipc.Semaphore) and
                isinstance(self.sem_cond, sysv_ipc.Semaphore))


class Error(Enum):
    SSM_ERROR_FUTURE = -1
    SSM_ERROR_PAST = -2
    SSM_ERROR_NO_DATA = -3


class MC(Enum):
    MC_NULL = 0

    MC_VERSION_GET = 1

    MC_INITIALIZE = 2
    MC_TERMINATE = 3

    MC_CREATE = 4
    MC_DESTROY = 5
    MC_OPEN = 6
    MC_CLOSE = 7

    MC_STREAM_PROPERTY_SET = 8
    MC_STREAM_PROPERTY_GET = 9

    MC_GET_TID = 10

    MC_STREAM_LIST_NUM = 11
    MC_STREAM_LIST_INFO = 12
    MC_STREAM_LIST_NAME = 13

    MC_NODE_LIST_NUM = 14
    MC_NODE_LIST_INFO = 15
    MC_EDGE_LIST_NUM = 16
    MC_EDGE_LIST_INFO = 17

    MC_OFFSET = 18
    MC_TCPCONNECTION = 19
    MC_UDPCONNECTION = 20
    MC_FAIL = 30

    MC_RES = 31


class SSMOpenMode(Enum):
    SSM_READ = 0x20
    SSM_WRITE = 0x40
    SSM_EXCLUSIVE = 0x80
    SSM_READ_BUFFER = 0xa0
    SSM_MODE_MASK = 0xf0


class SSMMsg(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("res_type", ctypes.c_long),
        ("cmd_type", ctypes.c_int),
        ("name", ctypes.c_char * SSM_SNAME_MAX),
        ("suid", ctypes.c_int),
        ("ssize", ctypes.c_size_t),
        ("hsize", ctypes.c_size_t),
        ("time", ctypes.c_double),
        ("saveTime", ctypes.c_double),
    ]

    def __repr__(self):
        return (f"SSMMsg(res_type={self.res_type}, cmd_type={self.cmd_type}, name={self.name}, suid={self.suid}, "
                f"ssize={self.ssize}, hsize={self.hsize}, time={self.time}, saveTime={self.saveTime})")


def clac_ssm_table(life: SSMTimeT, cycle: SSMTimeT) -> int:
    return int((float(SSM_BUFFER_MARGIN) * (life.time / cycle.time)) + SSM_MARGIN)


def clac_ssm_life(table_num: int, cycle: SSMTimeT) -> SSMTimeT:
    return SSMTimeT((table_num - SSM_MARGIN) * cycle.time / SSM_BUFFER_MARGIN)


# == TID functions =======================================================


def get_tid_top(ipc: IPC) -> int:
    try:
        encoded_tid_top = ipc.shm.read(ctypes.sizeof(ctypes.c_int), 0)
        tid_top = ctypes.c_int.from_buffer_copy(encoded_tid_top).value
    except sysv_ipc.ExistentialError:
        return Error.SSM_ERROR_NO_DATA.value

    return tid_top


def get_tid_bottom(ipc: IPC) -> int:
    try:
        encoded_tid_top = ipc.shm.read(ctypes.sizeof(ctypes.c_int), 0)
        tid_top = ctypes.c_int.from_buffer_copy(encoded_tid_top).value
        encoded_num = ipc.shm.read(ctypes.sizeof(ctypes.c_int), ctypes.sizeof(ctypes.c_int))
        num = ctypes.c_int.from_buffer_copy(encoded_num).value
    except sysv_ipc.ExistentialError:
        return Error.SSM_ERROR_NO_DATA.value

    tid_bottom = tid_top - num + SSM_MARGIN + 1
    return tid_bottom


def get_tid_time(ipc: IPC, ytime: SSMTimeT) -> Optional[int]:
    ssm_header = read_ssm_header(ipc)
    if not isinstance(ssm_header, SSMHeader):
        return None

    top = ssm_header.tid_top
    bottom = top - ssm_header.num + SSM_MARGIN + 1

    encoded_top_time = read_ssm_time(ipc, ssm_header, top)
    top_time = SSMTimeT.from_buffer_copy(encoded_top_time)
    encoded_bottom_time = read_ssm_time(ipc, ssm_header, bottom)
    bottom_time = SSMTimeT.from_buffer_copy(encoded_bottom_time)
    if ytime.time > top_time.time:
        return top
    if ytime.time < bottom_time.time:
        return Error.SSM_ERROR_PAST.value

    tid = top + int((ytime.time - top_time.time) / (int(ssm_header.cycle * get_time_ssm_speed())))

    if tid > top:
        tid = top
    elif tid < bottom:
        tid = bottom

    encoded_tid_time = read_ssm_time(ipc, ssm_header, tid)
    tid_time = SSMTimeT.from_buffer_copy(encoded_tid_time)
    while tid_time.time < ytime.time:
        tid += 1
        encoded_tid_time = read_ssm_time(ipc, ssm_header, tid)
        tid_time = SSMTimeT.from_buffer_copy(encoded_tid_time)
    while tid_time.time > ytime.time:
        tid -= 1
        encoded_tid_time = read_ssm_time(ipc, ssm_header, tid)
        tid_time = SSMTimeT.from_buffer_copy(encoded_tid_time)

    return tid


# =======================MSG functions=========================================


def send_msg(cmd_type: int, msg: SSMMsg) -> int:
    global msq, my_pid

    if not isinstance(msq, sysv_ipc.MessageQueue):
        err_ssm(f"MSQ err")
        return 0

    msg.res_type = my_pid
    msg.cmd_type = cmd_type

    try:
        msq.send(bytes(msg), type=MSQ_CMD)
    except sysv_ipc.Error as e:
        err_ssm(f"msgsnd error: {e}")
        exit(1)
    except OSError:
        exit(1)

    return 1


def receive_msg() -> Union[SSMMsg, int]:
    global msq, my_pid
    if not isinstance(msq, sysv_ipc.MessageQueue):
        err_ssm(f"MSQ err")
        return 0

    encoded_msg = msq.receive(type=my_pid)
    msg = SSMMsg.from_buffer_copy(encoded_msg[0])

    return msg


def communicate_msg(cmd_type: int, msg: SSMMsg) -> Union[SSMMsg, int]:
    send_msg(cmd_type, msg)
    msg = receive_msg()

    if not msg:
        return 0

    return msg


# =======================API functions=========================================


def err_ssm(err_msg):
    sys.stderr.write(f"SSM Err: {err_msg}\n")


def init_ssm() -> int:
    global msq, my_pid
    try:
        msq = sysv_ipc.MessageQueue(MSQ_KEY, mode=0o666)
    except sysv_ipc.ExistentialError:
        err_ssm(f"Failed to open MSQ queue: {MSQ_KEY}")
        return 0

    if msq is None:
        err_ssm(f"Failed to open MSQ queue: {MSQ_KEY}")
        return 0

    my_pid = os.getpid()

    if not open_time_ssm():
        err_ssm(f"Failed to open Time SSM")
        return 0

    if not send_msg(MC.MC_INITIALIZE.value, SSMMsg()):
        err_ssm(f"Failed to send Msg")
        return 0

    return 1


def end_ssm() -> int:
    global msq, my_pid
    ret = 1

    if send_msg(MC.MC_TERMINATE.value, SSMMsg()) == 0:
        ret = 0

    close_time_ssm()

    return ret


# ------------Allocate sensor data space with timetable on SSM  -----


def create_ssm(name: str, stream_id: int, ssm_size: int, life: SSMTimeT, cycle: SSMTimeT) -> Optional[IPC]:
    global msq, my_pid

    open_mode = SSMOpenMode.SSM_READ.value | SSMOpenMode.SSM_WRITE.value

    len_name = len(name)
    if len_name == 0 or len_name >= SSM_SNAME_MAX:
        err_ssm(f"create : stream name length of '{name}' err.\n")
        return None

    if stream_id < 0:
        err_ssm("create : stream id err.\n")
        return None

    if life.time <= 0.0:
        err_ssm("create : stream life time err.\n")

    if cycle.time <= 0.0:
        err_ssm("create : stream cycle err.\n")
        return None

    if life.time < cycle.time:
        err_ssm("create : stream saveTime MUST be larger than stream cycle.\n")
        return None

    msg = SSMMsg()
    msg.name = name.encode('utf-8')
    msg.suid = stream_id
    msg.ssize = ssm_size
    msg.hsize = clac_ssm_table(life, cycle)
    msg.time = cycle.time
    msg = communicate_msg(MC.MC_CREATE.value | open_mode, msg)

    if not msg:
        return None

    if not msg.suid:
        return None

    shm = shm_open_ssm(msg.suid)

    if not isinstance(shm, sysv_ipc.SharedMemory):
        return None

    try:
        encoded_header_data = shm.read(ctypes.sizeof(SSMHeader))
        ssm_header = SSMHeader.from_buffer_copy(encoded_header_data)
    except sysv_ipc.ExistentialError:
        return None

    sem_lock = sem_open_ssm(ssm_header.sem_lock_key)
    sem_cond = sem_open_ssm(ssm_header.sem_cond_key)

    return IPC(shm, sem_lock, sem_cond)


def release_ssm(ipc: IPC) -> int:
    return shm_release_ssm(ipc.shm)


# ----------------------Open sensor data on SSM-----------------


def open_ssm(name: str, stream_id: int, open_mode: SSMOpenMode) -> Optional[IPC]:
    len_name = len(name)
    if len_name == 0 or len_name >= SSM_SNAME_MAX:
        err_ssm(f"create : stream name length of '{name}' err.\n")
        return None

    if stream_id < 0:
        err_ssm("create : stream id err.\n")
        return None

    msg = SSMMsg()
    msg.name = name.encode('utf-8')
    msg.suid = stream_id
    msg = communicate_msg(MC.MC_OPEN.value | open_mode.value, msg)

    if not msg:
        return None

    if msg.suid < 0:
        return None

    shm = shm_open_ssm(msg.suid)

    try:
        encoded_header_data = shm.read(ctypes.sizeof(SSMHeader))
        ssm_header = SSMHeader.from_buffer_copy(encoded_header_data)
    except sysv_ipc.ExistentialError:
        return None

    sem_lock = sem_open_ssm(ssm_header.sem_lock_key)
    sem_cond = sem_open_ssm(ssm_header.sem_cond_key)

    return IPC(shm, sem_lock, sem_cond)


def close_ssm(ipc: IPC) -> int:
    return shm_close_ssm(ipc.shm)


# ----------------------Read ssm data on SSM-----------------


def read_ssm_header(ipc: IPC) -> Optional[SSMHeader]:
    try:
        encoded_header_data = ipc.shm.read(ctypes.sizeof(SSMHeader))
        ssm_header = SSMHeader.from_buffer_copy(encoded_header_data)
    except sysv_ipc.ExistentialError:
        exit(1)

    return ssm_header


def read_ssm_data(ipc: IPC, ssm_header: SSMHeader, tid: int) -> Optional[bytes]:
    data_pos = ssm_header.data_off + ((tid % ssm_header.num) * ssm_header.size)
    try:
        encoded_ssm_data = ipc.shm.read(ssm_header.size, data_pos)
    except sysv_ipc.ExistentialError:
        exit(1)

    return encoded_ssm_data


def read_ssm_time(ipc: IPC, ssm_header: SSMHeader, tid: int) -> Optional[bytes]:
    time_pos = ssm_header.times_off + ((tid % ssm_header.num) * ctypes.sizeof(SSMTimeT))
    try:
        encoded_ssm_time = ipc.shm.read(ctypes.sizeof(SSMTimeT), time_pos)
    except sysv_ipc.ExistentialError:
        exit(1)

    return encoded_ssm_time


# ----------------------Read sensor data on SSM-----------------


def read_ssm(ipc: IPC, tid: int) -> Union[Tuple[SSMHeader, bytes, bytes], Error]:
    top = get_tid_top(ipc)
    bottom = get_tid_bottom(ipc)

    if tid < 0:
        tid = top

    if tid < SSM_TID_SP:
        return Error.SSM_ERROR_NO_DATA
    if tid > top:
        return Error.SSM_ERROR_FUTURE
    if tid < bottom:
        return Error.SSM_ERROR_PAST

    ssm_header = read_ssm_header(ipc)
    if not isinstance(ssm_header, SSMHeader):
        return Error.SSM_ERROR_NO_DATA

    encoded_ssm_data = read_ssm_data(ipc, ssm_header, tid)
    encoded_ssm_time = read_ssm_time(ipc, ssm_header, tid)

    return ssm_header, encoded_ssm_data, encoded_ssm_time


def read_time_ssm(ipc: IPC, ytime: SSMTimeT) -> Union[Tuple[SSMHeader, bytes, bytes], Error]:
    if ytime.time <= 0:
        tid = -1
    else:
        tid = get_tid_time(ipc, ytime)
        if tid < 0:
            return Error.SSM_ERROR_NO_DATA

    return read_ssm(ipc, tid)


# ----------------------Write sensor data on SSM-----------------


def write_ssm(ipc: IPC, data: bytes, ytime: bytes) -> Optional[int]:
    ssm_header = read_ssm_header(ipc)
    if not isinstance(ssm_header, SSMHeader):
        return None

    ssm_header.tid_top += 1
    data_pos = ssm_header.data_off + (ssm_header.tid_top % ssm_header.num) * ssm_header.size
    time_pos = ssm_header.times_off + (ssm_header.tid_top % ssm_header.num) * ctypes.sizeof(SSMTimeT)

    try:
        ipc.sem_lock.acquire()
        ipc.shm.write(data, offset=data_pos)
        ipc.shm.write(ytime, offset=time_pos)
        ipc.shm.write(bytearray((ctypes.c_int * 1)(ssm_header.tid_top)), offset=0)
        ipc.sem_lock.release()
    except sysv_ipc.ExistentialError:
        exit(1)

    cond_wait = ipc.sem_cond.waiting_for_nonzero
    if cond_wait > 0:
        ipc.sem_cond.release(cond_wait)

    return ssm_header.tid_top


# ----------------------Wait for new sensor data on SSM-----------------


def wait_tid_ssm(ipc: IPC, tid: int) -> Optional[int]:
    tid_top = get_tid_top(ipc)
    while tid > tid_top:
        try:
            ipc.sem_cond.acquire()
        except sysv_ipc.ExistentialError:
            exit(1)
        tid_top = get_tid_top(ipc)

    return tid_top


# ----------------------Property setting-----------------


def set_property_ssm(name: str, sensor_uid: int, data: bytes, size: int) -> Optional[int]:
    global msq, my_pid

    if not isinstance(msq, sysv_ipc.MessageQueue):
        err_ssm(f"MSQ err")
        return None

    len_name = len(name)
    if len_name == 0 or len_name >= SSM_SNAME_MAX:
        err_ssm(f"name length\n")
        return None

    msg = SSMMsg()
    msg.name = name.encode('utf-8')
    msg.suid = sensor_uid
    msg.ssize = size
    msg.hsize = 0
    msg.time = 0

    msg = communicate_msg(MC.MC_STREAM_PROPERTY_SET.value, msg)

    if not msg:
        return None

    if not msg.ssize:
        return None

    try:
        msq.send(data, type=msg.res_type)
    except sysv_ipc.Error as e:
        print("msgsnd error:", e)
        return None

    return 1


def get_property_ssm(name: str, sensor_uid: int) -> Optional[Tuple[str, int]]:
    global msq, my_pid

    if not isinstance(msq, sysv_ipc.MessageQueue):
        err_ssm(f"MSQ err")
        return None

    len_name = len(name)
    if len_name == 0 or len_name >= SSM_SNAME_MAX:
        err_ssm(f"name length\n")
        return None

    msg = SSMMsg()
    msg.name = name.encode('utf-8')
    msg.suid = sensor_uid
    msg.ssize = 0
    msg.hsize = 0
    msg.time = 0

    msg = communicate_msg(MC.MC_STREAM_PROPERTY_GET.value, msg)

    if not msg:
        return None

    if not msg.ssize:
        return None
    size = msg.ssize

    received_data = msq.receive(type=my_pid)

    return received_data[0], size


