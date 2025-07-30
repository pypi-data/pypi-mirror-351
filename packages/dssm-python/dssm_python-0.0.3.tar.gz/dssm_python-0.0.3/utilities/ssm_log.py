import io
from typing import BinaryIO

from dssm_python.libssm import *


def is_good(log_file: BinaryIO):
    if log_file.closed:
        return False

    try:
        current_position = log_file.tell()
        log_file.seek(current_position)
        return True
    except Exception:
        return False

class SSMLogBase:
    def __init__(self, m_time=None, m_data=None, m_data_size=0, m_property=None, m_property_size=0, m_stream_id=0,
                 m_buffer_num=0, m_cycle=0.0, m_start_time=SSMTimeT(0.0), m_log_file=None, m_stream_name="",
                 m_start_pos=0, m_end_pos=0, m_property_pos=0):
        self.__m_time__: SSMTimeT = m_time
        self.__m_data__: any = m_data
        self.__m_data_size__: int = m_data_size
        self.__m_property__: any = m_property
        self.__m_property_size__: int = m_property_size
        self.__m_stream_id__: int = m_stream_id
        self.__m_buffer_num__: int = m_buffer_num
        self.__m_cycle__: float = m_cycle
        self.__m_start_time__: SSMTimeT = m_start_time

        self.__m_log_file__: Optional[BinaryIO] = m_log_file
        self.__m_stream_name__: str = m_stream_name
        self.__m_start_pos__: any = m_start_pos
        self.__m_end_pos__: any = m_end_pos
        self.__m_property_pos__: any = m_property_pos

    def __repr__(self):
        return (f"SSMLogBase(m_time={self.__m_time__}, m_data={self.__m_data__}, m_data_size={self.__m_data_size__}, "
                f"m_property={self.__m_property__}, m_property_size={self.__m_property_size__}, "
                f"m_stream_id={self.__m_stream_id__}, m_buffer_num={self.__m_buffer_num__}, m_cycle={self.__m_cycle__}, "
                f"m_start_time={self.__m_start_time__}, m_log_file={self.__m_log_file__}, "
                f"m_stream_name={self.__m_stream_name__}, m_start_pos={self.__m_start_pos__}, "
                f"m_end_pos={self.__m_end_pos__}, m_property_pos={self.__m_property_pos__})")

    def __write_property__(self):
        if self.__m_log_file__ is None or self.__m_property__ is None or self.__m_property_size__ == 0:
            return False

        try:
            self.__m_log_file__.seek(0, 1)
            cur_pos = self.__m_log_file__.tell()

            self.__m_log_file__.seek(self.__m_property_pos__, 0)
            self.__m_log_file__.write(self.__m_property__[:self.__m_property_size__])

            self.__m_log_file__.seek(cur_pos, 0)
        except Exception as e:
            print(f"SSMLogBase::write_property() : error writing property - {e}")
            return False

        return True

    def __get_log_info__(self):
        if self.__m_log_file__ is None:
            return False

        try:
            self.__m_log_file__.seek(0, io.SEEK_SET)
            line = self.__m_log_file__.readline().decode('utf-8')
            if not line:
                return False

            data = io.StringIO(line)
            tokens = data.read().split()
            if len(tokens) < 7:
                return False

            self.__m_stream_name__ = tokens[0]
            self.__m_stream_id__ = int(tokens[1])
            self.__m_data_size__ = int(tokens[2])
            self.__m_buffer_num__ = int(tokens[3])
            self.__m_cycle__ = float(tokens[4])
            self.__m_start_time__ = SSMTimeT(float(tokens[5]))
            self.__m_property_size__ = int(tokens[6])

            self.__m_property_pos__ = self.__m_log_file__.tell()
            if self.__m_property__ is not None:
                self.read_property()

            self.__m_log_file__.seek(self.__m_property_size__, io.SEEK_CUR)

            self.__m_start_pos__ = self.__m_log_file__.tell()
            self.__m_log_file__.seek(0, io.SEEK_END)
            self.__m_end_pos__ = self.__m_log_file__.tell()
            self.__m_log_file__.seek(self.__m_start_pos__)

            self.__m_time__ = self.__m_start_time__
        except Exception as e:
            print(f"SSMLogBase::get_log_info() : error reading log info - {e}")
            return False

        return True

    def __set_log_info__(self, start_time):
        if self.__m_log_file__ is None:
            return False

        try:
            self.__m_log_file__.seek(0, io.SEEK_SET)
            self.__m_start_time__ = start_time
            log_info = (
                f"{self.__m_stream_name__} {self.__m_stream_id__} {self.__m_data_size__} {self.__m_buffer_num__} "
                f"{self.__m_cycle__} {self.__m_start_time__} {self.__m_property_size__}\n")
            self.__m_log_file__.write(log_info.encode('utf-8'))

            self.__m_property_pos__ = self.__m_log_file__.tell()

            self.__write_property__()

            self.__m_log_file__.seek(self.__m_property_size__, io.SEEK_CUR)

            self.mStartPos = self.__m_log_file__.tell()

            self.__m_log_file__.seek(self.mStartPos)
        except Exception as e:
            print(f"SSMLogBase::set_log_info() : error setting log info - {e}")
            return False

        return True

    def set_buffer(self, data, data_size, log_property, property_size):
        self.__m_data__ = data
        self.__m_data_size__ = data_size
        self.__m_property__ = log_property
        self.__m_property_size__ = property_size

    def read_property(self):
        if self.__m_log_file__ is None or self.__m_property__ is None or self.__m_property_size__ == 0:
            return False

        try:
            cur_pos = self.__m_log_file__.tell()

            self.__m_log_file__.seek(self.__m_property_pos__, io.SEEK_SET)
            self.__m_property__ = self.__m_log_file__.read(self.__m_property_size__)

            self.__m_log_file__.seek(cur_pos, io.SEEK_SET)
        except Exception as e:
            print(f"SSMLogBase::read_property() : error reading property - {e}")
            return False

        return True

    def open(self, file_name):
        try:
            self.__m_log_file__ = open(file_name, 'rb')
        except IOError as e:
            print(f"SSMLogBase::open : cannot open log file '{file_name}'.")
            return False

        if not self.__m_log_file__:
            print(f"SSMLogBase::open : cannot open log file '{file_name}'.")
            return False

        if not self.__get_log_info__():
            print(f"SSMLogBase::open : '{file_name}' is NOT an ssm-log file.")
            return False

        return True

    def create(self, stream_name, stream_id, buffer_num, cycle, file_name, start_time: SSMTimeT = None):
        if start_time is None:
            start_time = get_time_ssm()

        try:
            self.__m_log_file__ = open(file_name, 'wb')
        except IOError as e:
            print(f"SSMLogBase::create() : cannot create log file '{file_name}'.")
            return False

        self.__m_stream_name__ = stream_name
        self.__m_stream_id__ = stream_id
        self.__m_buffer_num__ = buffer_num
        self.__m_cycle__ = cycle
        self.__m_start_time__ = start_time

        if not self.__m_log_file__:
            print(f"SSMLogBase::create() : cannot create log file '{file_name}'.")
            return False

        if not self.__set_log_info__(start_time):
            print(f"SSMLogBase::create() : cannot write ssm-info to '{file_name}'.")
            self.close()
            return False

        return True

    def close(self):
        if self.__m_log_file__ is not None:
            self.__m_log_file__.close()
            self.__m_log_file__ = None
        return True

    def write(self, ssm_time: SSMTimeT = None):
        if self.__m_log_file__ is None or self.__m_data__ is None or self.__m_data_size__ == 0:
            return False

        if ssm_time is None:
            ssm_time = get_time_ssm()

        try:
            self.__m_time__ = ssm_time
            self.__m_log_file__.write(struct.pack('d', self.__m_time__))
            self.__m_log_file__.write(self.__m_data__[:self.__m_data_size__])
        except Exception as e:
            print(f"SSMLogBase::write() : error writing to log file - {e}")
            return False

        return True

    def read(self):
        if self.__m_log_file__ is None or self.__m_data__ is None or self.__m_data_size__ == 0:
            return False

        try:
            time_data = self.__m_log_file__.read(ctypes.sizeof(SSMTimeT))
            if not time_data:
                return False
            self.__m_time__ = SSMTimeT.from_buffer_copy(time_data)
            self.__m_data__ = self.__m_log_file__.read(self.__m_data_size__)
            if not self.__m_data__:
                return False
        except Exception as e:
            print(f"SSMLogBase::read() : error reading from log file - {e}")
            return False

        return True

    def seek(self, diff):
        if self.__m_log_file__ is None:
            return False

        try:
            self.__m_log_file__.seek(0, io.SEEK_CUR)
            cur_pos = self.__m_log_file__.tell()

            seek_pos = cur_pos + (ctypes.sizeof(SSMTimeT) + self.__m_data_size__) * diff
            self.__m_log_file__.seek(seek_pos, io.SEEK_SET)

            pos = self.__m_log_file__.tell()
            if pos < self.__m_start_pos__ or pos > self.__m_end_pos__:
                self.__m_log_file__.seek(cur_pos, io.SEEK_SET)
                return False
        except Exception as e:
            print(f"SSMLogBase::seek() : error seeking in log file - {e}")
            return False

        return True

    def read_time(self, ssm_time: SSMTimeT = None):
        if self.__m_log_file__ is None:
            return False

        try:
            cur_pos = self.__m_log_file__.tell()

            if not self.seek(int((ssm_time.time - self.__m_time__.time) / self.__m_cycle__)):
                self.__m_log_file__.seek(cur_pos, io.SEEK_SET)
                return False

            if not (self.read_next() or self.read_back()):
                self.__m_log_file__.seek(cur_pos, io.SEEK_SET)
                return False

            self.__m_log_file__.seek(0, io.SEEK_CUR)
            while self.__m_time__ < ssm_time and self.read_next():
                pass
            self.__m_log_file__.seek(0, io.SEEK_CUR)
            while self.__m_time__ >= ssm_time and self.read_back():
                pass
        except Exception as e:
            print(f"SSMLogBase::read_time() : error reading time - {e}")
            return False

        return True

    def read_next(self):
        return self.read()

    def read_back(self):
        return self.seek(-2) and self.read()
