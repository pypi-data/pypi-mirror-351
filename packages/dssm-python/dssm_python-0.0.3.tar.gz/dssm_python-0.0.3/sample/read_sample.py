import signal

from dssm_python.ssm import *
from sample_datastruct import *

keep_running = True


def signal_handler(sig, frame):
    global keep_running
    print('Loop interrupted by Ctrl-C')
    keep_running = False


if __name__ == "__main__":
    if not init_ssm():
        print("failed to initialize ssm")
        exit(1)

    ssm_api = SSMBaseAPI(stream_name='intSsm', stream_id=1, data_size=ctypes.sizeof(IniSsm), data_struct=IniSsm,
                         m_property_size=ctypes.sizeof(IniSsmProperty), property_struct=IniSsmProperty , is_blocking=True)

    if not ssm_api.open(SSMOpenMode.SSM_READ):
        print("failed to open ssm api")
        exit(1)

    print(ssm_api)
    ssm_api.get_property()
    print(ssm_api.__m_property__)

    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl-C to stop the loop.')

    ssm_api.read()

    tid = -1
    while keep_running:
        # read just new data
        if ssm_api.read_new():
            print(ssm_api.__data__)
            print(ssm_api.__time__)

        # read by tid
        # if ssm_api.read(tid):
        #     tid = ssm_api.__time_id__
        #     print(ssm_api.__data__)
        #     print(ssm_api.__time__)

        # read by time
        # ytime = get_time_ssm().time - 3
        # if ssm_api.read_time(SSMTimeT(ytime)):
        #     print(ssm_api.__data__)
        #     print(ssm_api.__time__)

        sleep_ssm(1)

    ssm_api.close()
    end_ssm()
