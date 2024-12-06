import hid
import time

def connect_device():
    try:
        # デバイスをVIDとPIDに基づいてオープン
        device = hid.device()
        device.open(0x046d, 0xc218)  # Logitech RumblePad 2のVIDとPID
        print("デバイスに接続しました: Logitech RumblePad 2 USB")
        return device
    except IOError as e:
        print(f"デバイス接続に失敗しました: {e}")
        return None

def read_device_data(device):
    try:
        print("デバイスからのデータを待っています...")
        data = device.read(8)  # 8バイトのデータを読み取ります
        if data:
            print("受信データ:", data)
        else:
            print("データを受信できませんでした。")
    except IOError as e:
        print(f"デバイス読み取りエラー: {e}")

# 実行
device = connect_device()
if device:
    read_device_data(device)
    device.close()  # 使用後は必ずデバイスを閉じます
else:
    print("デバイスが見つからないため、プログラムを終了します。")
