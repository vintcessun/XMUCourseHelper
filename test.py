import subprocess
import threading
import json
import time


class WebsocatWrapper:
    def __init__(self, url, cookie):
        self.url = url
        self.cookie = cookie
        self.process = None
        self.is_running = False

    def start(self):
        # 构造你之前成功的 websocat 命令
        cmd = [
            "websocat",
            self.url,
            "-H",
            f"Origin: https://xk.xmu.edu.cn",
            "-H",
            f"Cookie: {self.cookie}",
            "-H",
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "--text",
            "--insecure",  # 相当于 sslopt CERT_NONE
        ]

        print(f"🚀 启动驱动: {' '.join(cmd)}")

        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # 行缓冲
            encoding="utf-8",
        )
        self.is_running = True

        # 启动读取线程
        threading.Thread(target=self._read_output, daemon=True).start()

    def _read_output(self):
        while self.is_running:
            line = self.process.stdout.readline()
            if line:
                print(f"📥 收到数据: {line.strip()}")
                # 这里可以回调你的业务逻辑
            else:
                break
        print("❌ websocat 驱动已停止")

    def send(self, msg):
        if self.process and self.process.stdin:
            print(f"📤 发送指令: {msg}")
            self.process.stdin.write(f"{msg}\n")
            self.process.stdin.flush()


# --- 测试代码 ---
if __name__ == "__main__":
    # 使用你抓取的最新 Cookie
    MY_COOKIE = "route=4c0e9e958d8834bcfc1cbbe13b1bcb20; Authorization=..."
    WS_URL = "wss://xk.xmu.edu.cn/xsxkxmu/websocket/34520242201240"

    driver = WebsocatWrapper(WS_URL, MY_COOKIE)
    driver.start()

    time.sleep(2)  # 等待握手
    driver.send("hi")  # 发送心跳

    # 保持主线程运行
    while True:
        time.sleep(1)
