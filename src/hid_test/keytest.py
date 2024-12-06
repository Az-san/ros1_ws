import os

device_path = "/dev/hidraw0"  # ゲームパッドのデバイスパス

# 右十字ボタンのデータパターンをマッピング
right_dpad_mapping = {
    "8800": "4",    # Up
    "2800": "2",  # Down
    "4800": "3", # Right
    "1800": "1"   # Left
}

# 押していない状態のデータ
neutral_data = "0800"  # 押していないときのデータを「0800」に設定

try:
    with open(device_path, "rb") as hid_device:
        print("Waiting for directional input...")

        while True:
            data = hid_device.read(8).hex()  # 16進数データとして読み取り
            right_dpad_data = data[8:12]    # 右十字ボタンの該当データ位置

            # 無入力状態（neutral_data）の場合は何も表示しない
            if right_dpad_data == neutral_data:
                continue

            # 入力がある場合のみ方向を判定
            if right_dpad_data in right_dpad_mapping:
                direction = right_dpad_mapping[right_dpad_data]
                print(f"Right D-Pad Direction: {direction}")

except FileNotFoundError:
    print(f"Device {device_path} not found.")
except PermissionError:
    print(f"Permission denied for device {device_path}. Try 'sudo chmod 666 {device_path}'")
