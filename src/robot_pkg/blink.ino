void setup() {
  pinMode(13, OUTPUT); // LEDピンを出力モードに設定
}

void loop() {
  digitalWrite(13, HIGH); // LED ON
  delay(1000);            // 1秒待機
  digitalWrite(13, LOW);  // LED OFF
  delay(1000);            // 1秒待機
}
