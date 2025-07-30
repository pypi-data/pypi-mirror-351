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

    ssm_api = SSMBaseAPI(stream_name='sample', stream_id=2, data_size=ctypes.sizeof(SampleSsm),
                         m_property_size=ctypes.sizeof(SampleSsmProperty), m_property=SampleSsmProperty)

    if not ssm_api.create(5.0, 1.0):
        print("failed to create ssm api")
        exit(1)

    property_ssm = SampleSsmProperty(5, 2.2, 'test Property'.encode("utf-8"))
    ssm_api.__m_property__ = property_ssm
    ssm_api.set_property()

    signal.signal(signal.SIGINT, signal_handler)
    print('Press Ctrl-C to stop the loop.')

    i = 1
    while keep_running:
        # for the sample_datastruct
        arr = [i+1, i+2, i+3, i+4, i+5]
        data = SampleSsm(i, i-1, 2.0, (ctypes.c_int * 5) (*arr) )
        data.array2d[0][1] = 5
        data.array2d[1][3] = 5
        data.array2d[2][0] = 5

        ssm_api.__data__ = data
        if ssm_api.write():
            print(i)
        i += 1

        sleep_ssm(1)

    ssm_api.release()
    end_ssm()