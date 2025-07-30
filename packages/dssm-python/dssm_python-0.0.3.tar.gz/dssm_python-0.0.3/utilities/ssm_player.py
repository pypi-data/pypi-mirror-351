import argparse
import shlex
import signal
import sys
import os
import fcntl
import logging
from datetime import datetime
from math import inf
from typing import List

from dssm_python.libssm import init_ssm, clac_ssm_life, end_ssm
from dssm_python.libssm_time import *
from dssm_python.ssm import SSMBaseAPI
from utilities.ssm_log import SSMLogBase

keep_running = True


def signal_handler(sig, frame):
    global keep_running
    print('Loop interrupted by Ctrl-C')
    keep_running = False


def get_unit(data):
    i = 0
    table = " kMGTPEZY"
    base = 1024.0

    while data >= base and i < len(table) - 1:
        data /= base
        i += 1

    unit = table[i]

    if 0 < i <= len(table) - 1:
        return data, unit
    return data, unit


class LogPlayer:
    def __init__(self):
        self.log_name: Optional[str] = None
        self.data: bytes = bytes()
        self.data_size: int = 0
        self.m_property: bytes = bytes()
        self.m_property_size: int = 0
        self.stream: SSMBaseAPI = SSMBaseAPI()
        self.ssm_log: SSMLogBase = SSMLogBase()
        self.read_cnt: int = 0
        self.write_cnt: int = 0
        self.m_is_playing: bool = False

    def __repr__(self):
        return (f"log_name: {self.log_name}, data: {self.data}, data_size: {self.data_size}, "
                f"m_property: {self.m_property}, m_property_size: {self.m_property_size}, stream: {self.stream}, "
                f"log: {self.ssm_log}, read_cnt: {self.read_cnt}, write_cnt: {self.write_cnt}, "
                f"m_is_playing: {self.m_is_playing}")

    def open(self) -> bool:
        logging.info(f"open: {self.log_name}")
        if not self.ssm_log.open(self.log_name):
            return False

        self.data_size = self.ssm_log.__m_data_size__
        self.m_property_size = self.ssm_log.__m_property_size__
        self.data = bytes(self.data_size)
        self.m_property = bytes(self.m_property_size)

        if self.data is None or (self.m_property_size and self.m_property is None):
            self.ssm_log.close()
            self.data = None
            self.m_property = None
            return False

        self.ssm_log.set_buffer(self.data, self.data_size, self.m_property, self.m_property_size)
        self.stream.set_buffer(self.data, self.data_size, self.m_property, self.m_property_size)

        self.ssm_log.read_property()
        self.ssm_log.read_next()

        save_time = clac_ssm_life(self.ssm_log.__m_buffer_num__, SSMTimeT(self.ssm_log.__m_cycle__))
        logging.info(f"> {self.ssm_log.__m_stream_name__}, {self.ssm_log.__m_stream_id__}, "
                     f"{save_time}, {self.ssm_log.__m_cycle__}")

        self.stream.__stream_name__ = self.ssm_log.__m_stream_name__
        self.stream.__stream_id__ = self.ssm_log.__m_stream_id__
        self.stream.__m_property__ = self.ssm_log.__m_property__
        self.stream.__m_property_size__ = self.ssm_log.__m_property_size__

        if not self.stream.create(save_time.time, self.ssm_log.__m_cycle__):
            return False

        if self.m_property_size and not self.stream.set_property():
            return False

        return True

    def close(self):
        self.stream.release()
        self.ssm_log.close()

    def seek(self, ssm_time: SSMTimeT) -> bool:
        if not self.ssm_log.read_time(ssm_time):
            return False
        if not self.stream.write(self.ssm_log.__m_time__):
            return False
        self.read_cnt += 1
        self.write_cnt = self.read_cnt
        return True

    def play(self, ssm_time: SSMTimeT = get_time_ssm()) -> bool:
        if self.read_cnt == self.write_cnt:
            self.m_is_playing = self.ssm_log.read_next()
            if self.m_is_playing:
                self.read_cnt += 1

        if self.ssm_log.__m_time__.time <= ssm_time.time and self.write_cnt < self.read_cnt:
            self.stream.__data__ = self.ssm_log.__m_data__
            self.stream.write(self.ssm_log.__m_time__)
            self.write_cnt = self.read_cnt
            return True

        return False

    def play_back(self, ssm_time: SSMTimeT = None) -> bool:
        if ssm_time is None:
            ssm_time = get_time_ssm()

        if self.read_cnt == self.write_cnt:
            self.m_is_playing = self.ssm_log.read_back()
            if self.m_is_playing:
                self.read_cnt += 1

        if self.ssm_log.__m_time__.time >= ssm_time.time and self.write_cnt < self.read_cnt:
            self.stream.write(self.ssm_log.__m_time__)
            self.write_cnt = self.read_cnt
            return True

        return False


LogPlayerArray = List[LogPlayer]


class MyParam:
    def __init__(self):
        self.log_array: LogPlayerArray = []
        self.start_time: SSMTimeT = SSMTimeT(-1)
        self.end_time: SSMTimeT = SSMTimeT(-1)
        self.start_offset_time: SSMTimeT = SSMTimeT(0.0)
        self.end_offset_time: SSMTimeT = SSMTimeT(0.0)
        self.speed: float = 1.0
        self.is_loop: bool = False

    def print_help(self, argv):
        print("HELP")
        print("\t-x | --speed <SPEED>            : set playing speed to SPEED.")
        print("\t-s | --start-time <OFFSET TIME> : start playing log at TIME.")
        print("\t-e | --end-time <OFFSET TIME>   : end playing log at TIME.")
        print("\t-l | --loop                     : looping mode.")
        print("\t-S | --start-ssmtime <SSMTIME>  : start playing log at SSMTIME.")
        print("\t-E | --end-ssmtime <SSMTIME>    : end playing log at SSMTIME.")
        print("\t-v | --verbose                  : verbose.")
        print("\t-q | --quiet                    : quiet.")
        print("\t-h | --help                     : print help")
        print(f"ex)\n\t$ python3 {argv[0]} hoge1.log hoge2.log\n")

    def opt_analyze(self, argv) -> bool:
        parser = argparse.ArgumentParser(description="Analyze options for the script.", add_help=False)

        parser.add_argument('-x', '--speed', type=float, help='Set the speed')
        parser.add_argument('-s', '--start-time', type=float, help='Set the start offset time')
        parser.add_argument('-e', '--end-time', type=float, help='Set the end offset time')
        parser.add_argument('-l', '--loop', action='store_true', help='Enable loop mode')
        parser.add_argument('-S', '--start-ssmtime', type=float, help='Set the start SSM time')
        parser.add_argument('-E', '--end-ssmtime', type=float, help='Set the end SSM time')
        parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
        parser.add_argument('-q', '--quiet', action='store_true', help='Enable quiet mode')
        parser.add_argument('-h', '--help', action='store_true', help='Show help message and exit')
        parser.add_argument('logfiles', nargs='*', help='Log files to process')

        args = parser.parse_args(argv[1:])

        if args.help:
            self.print_help(argv)
            return False

        if args.speed is not None:
            self.speed = args.speed
        if args.start_time is not None:
            self.start_offset_time = SSMTimeT(args.start_time)
        if args.end_time is not None:
            self.end_offset_time = SSMTimeT(args.end_time)
        if args.loop:
            self.is_loop = True
        if args.start_ssmtime is not None:
            self.start_time = SSMTimeT(args.start_ssmtime)
        if args.end_ssmtime is not None:
            self.end_time = SSMTimeT(args.end_ssmtime)
        if args.verbose:
            logging.basicConfig(level=logging.INFO)
        if args.quiet:
            logging.basicConfig(level=logging.ERROR)

        for log_file in args.logfiles:
            log_player = LogPlayer()
            log_player.log_name = log_file
            self.log_array.append(log_player)

        if not self.log_array:
            logging.error("USAGE: this program needs <LOGFILE> of ssm.")
            logging.error(f"help: {argv[0]} -h")
            return False

        return True

    def log_open(self) -> bool:
        ssm_time = SSMTimeT(inf)

        set_time_ssm_is_pause(1)
        set_speed_ssm(self.speed)

        for log_player in self.log_array:
            if not log_player.open():
                self.log_array.remove(log_player)
                continue
            if log_player.ssm_log.__m_start_time__.time < ssm_time.time:
                ssm_time = log_player.ssm_log.__m_start_time__

        if self.start_time.time > 0 or self.start_offset_time.time > 0:
            if self.start_time.time <= 0:
                self.start_time = ssm_time
            self.start_time.time += self.start_offset_time.time

            self.seek(self.start_time)
        else:
            self.start_time = ssm_time

        if self.end_time.time > 0 or self.end_offset_time.time > 0:
            if self.end_time.time <= 0:
                self.end_time = ssm_time
            self.end_time.time += self.end_offset_time.time
        else:
            self.end_time = SSMTimeT(inf)

        logging.info(f"start_time : {self.start_time}")
        set_time_ssm(self.start_time)

        set_time_ssm_is_pause(0)

        return True

    def seek(self, ssm_time) -> bool:
        is_pause = get_time_ssm_is_pause()
        set_time_ssm_is_pause(1)
        for log_player in self.log_array:
            log_player.seek(ssm_time)
        set_time_ssm(ssm_time)
        set_time_ssm_is_pause(is_pause)
        return True

    def print_progress(self, ssm_time: SSMTimeT) -> bool:
        unit = ''
        total = 0.0

        day = datetime.fromtimestamp(ssm_time.time).strftime("%Y/%m/%d(%a) %H:%M:%S %Z")

        total, unit = get_unit(total)

        logging.info("\033[s")  # Save current cursor position
        logging.info("\033[6A")  # Move up 6 lines
        logging.info("\r\033[K")  # Clear line from the cursor right
        logging.info(f"\033[K------[ {day} ]-------------")
        logging.info(f"\033[Kssm time  : {ssm_time}")
        logging.info(f"\033[Klog time  : {ssm_time.time - self.start_time.time + self.start_offset_time.time}")
        logging.info(f"\033[Kspeed rate: {get_time_ssm_speed()}")
        logging.info("\033[K")
        logging.info("\033[u")  # Restore cursor position

        return True

    def command_analyze(self, a_command) -> bool:
        global keep_running

        data = shlex.split(a_command)
        if not data:
            return False

        command = data[0]
        if command in ("speed", "x"):
            speed = float(data[1]) if len(data) > 1 else 1.0
            set_speed_ssm(speed)
        elif command == "skip":
            skip = float(data[1]) if len(data) > 1 else 0.1
            set_time_ssm(get_time_ssm().time + skip)
        elif command == "seek":
            offset = float(data[1]) if len(data) > 1 else 0.0
            self.seek(get_time_ssm().time + offset)
        elif command in ("pause", "p"):
            set_time_ssm_is_pause(1)
        elif command in ("start", "s"):
            set_time_ssm_is_pause(0)
        elif command in ("reverse", "r"):
            set_speed_ssm(-get_time_ssm_speed())
        elif command in ("quit", "q"):
            keep_running = False
        else:
            for c in command:
                if c == '+':
                    set_speed_ssm(get_time_ssm_speed() * 1.2)
                elif c == '-':
                    set_speed_ssm(get_time_ssm_speed() / 1.2)
                elif c == '>':
                    set_time_ssm_is_pause(1)
                    set_time_ssm(get_time_ssm().time + 0.1)

        logging.info("\033[2A\033[1M\r \n\r\033[K> ")
        return True


if __name__ == "__main__":
    param = MyParam()

    if not param.opt_analyze(sys.argv):
        exit(-1)

    if not init_ssm():
        print("failed to initialize ssm")
        exit(1)

    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl-C to stop the loop.')

    try:
        fd = sys.stdin.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        param.log_open()

        logging.info("  start\n\n")
        logging.info("\033[1A" + "> ")

        print_time = get_time_ssm_real()

        while keep_running:
            is_working = False
            play_cnt = 0
            current_time = get_time_ssm()

            for log_player in param.log_array:
                is_working = log_player.play(current_time) if get_time_ssm_speed() >= 0 else log_player.play_back(
                    current_time)
                if log_player.m_is_playing:
                    play_cnt += 1

            if not play_cnt or current_time.time > param.end_time.time:
                if param.is_loop:
                    param.seek(param.start_time)
                else:
                    keep_running = False
                    break

            if get_time_ssm_real().time >= print_time.time:
                print_time.time += 1.0
                param.print_progress(current_time)

            try:
                command = sys.stdin.read(1)
                if command:
                    param.command_analyze(command.strip())
            except IOError:
                pass

            if not is_working:
                usleep_ssm(1000)

    except Exception as e:
        logging.error(f"EXCEPTION: {e}")

    logging.info("\nfinalize log data")
    for log_player in param.log_array:
        log_player.close()

    logging.info("ssm time init")
    init_time_ssm()

    logging.info("end")
    end_ssm()

    exit(0)
