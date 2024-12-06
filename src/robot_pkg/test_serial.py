import serial
import time

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # シリアル通信の設定
time.sleep(2)  # Arduinoのリセット待機時間
ser.write(b'1')  # Arduinoに'1'を送信
print("Sent '1' to Arduino")
response = ser.readline().decode().strip()  # Arduinoからの応答を取得
print(f"Response from Arduino: {response}")
