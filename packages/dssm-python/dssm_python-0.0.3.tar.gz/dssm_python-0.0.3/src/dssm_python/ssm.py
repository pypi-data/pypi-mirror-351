from dssm_python.libssm import *


class SSMBaseAPI:
    def __init__(self, stream_name="", stream_id=0, ssm_id=0, is_verbose=True, is_blocking=False, time_id=-1,
                 data=None, data_size=0, m_property=None, m_property_size=0, data_struct=None, property_struct=None):
        self.__stream_name__: str = stream_name
        self.__stream_id__: int = stream_id
        self.__ssm_id__: int = ssm_id
        self.__is_verbose__: bool = is_verbose
        self.__is_blocking__: bool = is_blocking
        self.__time_id__: int = time_id
        self.__header__: Optional[SSMHeader] = None
        self.__data__: Optional[data_struct] = data
        self.__data_size__: int = data_size
        self.__m_property__: Optional[property_struct] = m_property
        self.__m_property_size__: int = m_property_size
        self.__time__: Optional[SSMTimeT] = None
        self.ipc: Optional[IPC] = None
        self.data_struct: any = data_struct
        self.property_struct: any = property_struct

    def __repr__(self):
        return (
            f"SSMBaseAPI(stream_name={self.__stream_name__}, stream_id={self.__stream_id__}, ssm_id={self.__ssm_id__}, "
            f"is_verbose={self.__is_verbose__}, is_blocking={self.__is_blocking__}, time_id={self.__time_id__}, "
            f"data={self.__data__}, data_size={self.__data_size__}, m_property={self.__m_property__}, "
            f"m_property_size={self.__m_property_size__}, time={self.__time__}, ipc={self.ipc}))")

    def is_open(self) -> bool:
        return self.ipc is not None and self.ipc.is_open()

    def is_update(self) -> bool:
        if not self.is_open():
            return False

        tid = get_tid_top(self.ipc)
        return tid > self.__time_id__

    def create(self, save_time: float, cycle: float) -> bool:
        if not self.__data_size__:
            print(f"SSM::create() : data buffer of '{self.__stream_name__}', id = {self.__stream_id__} "
                  f"is not allocated.", file=sys.stderr)
            return False

        self.ipc = create_ssm(self.__stream_name__, self.__stream_id__, self.__data_size__,
                              SSMTimeT(save_time), SSMTimeT(cycle))

        if not self.is_open():
            if self.__is_verbose__:
                print(f"SSM::create() : cannot create '{self.__stream_name__}', id = {self.__stream_id__}",
                      file=sys.stderr)
            return False

        self.__ssm_id__ = self.ipc.shm.id

        return True

    def release(self) -> bool:
        if not self.is_open():
            return False
        self.ipc = None
        return True

    def open(self, open_mode: SSMOpenMode = SSMOpenMode.SSM_READ) -> bool:
        if not self.__data_size__:
            print(f"SSM::open() : data buffer of '{self.__stream_name__}', id = {self.__stream_id__} "
                  f"is not allocated.", file=sys.stderr)
            return False

        self.ipc = open_ssm(self.__stream_name__, self.__stream_id__, open_mode)

        if not self.is_open():
            if self.__is_verbose__:
                print(f"SSM::open() : cannot open '{self.__stream_name__}', "
                      f"id = {self.__stream_id__}, ipc: {self.ipc}",
                      file=sys.stderr)
            return False

        self.__ssm_id__ = self.ipc.shm.id

        return True

    def open_wait(self, timout: SSMTimeT = SSMTimeT(0.0), open_mode: SSMOpenMode = SSMOpenMode.SSM_READ) -> bool:
        if not self.__data_size__:
            print(f"SSM::open_wait() : data buffer of '{self.__stream_name__}', id = {self.__stream_id__} "
                  f"is not allocated.", file=sys.stderr)
            return False

        start = get_time_ssm_real()
        is_verbose = self.__is_verbose__
        self.__is_verbose__ = False

        ret = self.open(open_mode)
        if is_verbose and not ret:
            print(f"SSM::openWait() : wait for stream '{self.__stream_name__}', id = {self.__stream_id__}\n",
                  file=sys.stderr)

        while not ret and not sleep_ssm(1.0) and (
                timout.time <= 0 or get_time_ssm_real().time - start.time < timout.time):
            ret = self.open()

        self.__is_verbose__ = is_verbose

        if not ret:
            ret = self.open(open_mode)

        return ret

    def close(self) -> bool:
        if not self.is_open():
            return False
        if close_ssm(self.ipc) == 1:
            self.ipc = None
            return True
        else:
            return False

    def write(self, ssm_time: Optional[SSMTimeT] = None) -> bool:
        if not self.is_open():
            return False

        if ssm_time is None:
            ssm_time = get_time_ssm()

        tid = write_ssm(ipc=self.ipc, data=bytes(self.__data__), ytime=bytes(ssm_time))

        if tid is not None and tid >= 0:
            self.__time_id__ = tid
            self.__time__ = ssm_time
            return True
        return False

    def read(self, time_id: int = -1) -> bool:
        if not self.is_open():
            return False

        shm_data = read_ssm(ipc=self.ipc, tid=time_id)

        if isinstance(shm_data, Error):
            return False

        ssm_header, encoded_ssm_data, encoded_ssm_time = shm_data

        if self.data_struct is None:
            return False

        ssm_data = self.data_struct.from_buffer_copy(encoded_ssm_data)
        ssm_time = SSMTimeT.from_buffer_copy(encoded_ssm_time)

        if not isinstance(ssm_data, self.data_struct) or not isinstance(ssm_time, SSMTimeT):
            return False

        if ssm_header.tid_top >= 0:
            self.__time_id__ = ssm_header.tid_top
            self.__header__ = ssm_header
            self.__data__ = ssm_data
            self.__time__ = ssm_time
            return True

        return False

    def read_next(self, dt: int = 1) -> bool:
        if not self.is_open():
            return False

        tid_bottom = get_tid_bottom(self.ipc)

        if self.__time_id__ < 0:
            if self.__is_blocking__:
                if wait_tid_ssm(self.ipc, 0) is None:
                    return False
            self.read()

        rtid = self.__time_id__ + dt
        if rtid >= tid_bottom:
            if self.__is_blocking__:
                if wait_tid_ssm(self.ipc, rtid) is None:
                    return False
            return self.read(rtid)

        if self.__is_verbose__:
            print(f"SSM::readNext() : skipping read data '{self.__stream_name__}', "
                  f"id = {self.__stream_id__}, TID: {rtid} -> {tid_bottom}",
                  file=sys.stderr)

        return self.read(tid_bottom)

    def read_back(self, dt: int = 1) -> bool:
        return self.read(self.__time_id__ - dt) if dt <= self.__time_id__ else False

    def read_last(self) -> bool:
        return self.read()

    def read_new(self) -> bool:
        if not self.is_open():
            return False

        if self.__is_blocking__:
            if wait_tid_ssm(self.ipc, self.__time_id__ + 1) is None:
                return False

        return self.read(-1) if self.is_update() else False

    def read_time(self, ssm_time: SSMTimeT) -> bool:
        if not self.is_open():
            return False

        shm_data = read_time_ssm(self.ipc, ssm_time)

        if isinstance(shm_data, Error):
            return False

        ssm_header, encoded_ssm_data, encoded_ssm_time = shm_data

        if self.data_struct is None:
            return False

        ssm_data = self.data_struct.from_buffer_copy(encoded_ssm_data)
        ssm_time = SSMTimeT.from_buffer_copy(encoded_ssm_time)

        if not isinstance(ssm_data, self.data_struct) or not isinstance(ssm_time, SSMTimeT):
            return False

        if ssm_header.tid_top >= 0:
            self.__time_id__ = ssm_header.tid_top
            self.__header__ = ssm_header
            self.__data__ = ssm_data
            self.__time__ = ssm_time
            return True

        return False

    def set_property(self):
        if self.__m_property_size__ > 0:
            return bool(set_property_ssm(self.__stream_name__, self.__stream_id__, bytes(self.__m_property__),
                                         self.__m_property_size__))
        else:
            return False

    def get_property(self):
        if self.__m_property_size__ > 0:
            result = get_property_ssm(self.__stream_name__, self.__stream_id__)

            if result is not None:
                m_property_encoded, m_property_size = result

                if self.property_struct is None:
                    return False

                m_property = self.property_struct.from_buffer_copy(m_property_encoded)
                if isinstance(m_property, self.property_struct):
                    self.__m_property__ = m_property
                    self.__m_property_size__ = m_property_size
                    return True
            return False
        else:
            return False

    def set_buffer(self, data: any, data_size: int, m_property: any, m_property_size: int):
        self.__data__ = data
        self.__data_size__ = data_size
        self.__m_property__ = m_property
        self.__m_property_size__ = m_property_size

    def set_data_buffer(self, data: any, data_size: int):
        self.__data__ = data
        self.__data_size__ = data_size

    def set_property_buffer(self, m_property: any, m_property_size: int):
        self.__m_property__ = m_property
        self.__m_property_size__ = m_property_size
