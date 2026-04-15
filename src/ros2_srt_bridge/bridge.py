import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import socket
import json
import threading
import time

WIDTH = 640
HEIGHT = 480
FPS = 30

PC_IP = "10.143.239.237"

SRT_PORT = 9000
RTT_PORT = 9001

PASS = "PFE_secure_2026"

# ================= RTT CLIENT =================
class RTTClient(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(1.0)
        self.seq = 0

    def run(self):
        while True:
            self.seq += 1
            t0 = time.time()

            packet = {
                "type": "rtt_probe",
                "seq": self.seq,
                "t": t0
            }

            try:
                # send probe
                self.sock.sendto(json.dumps(packet).encode(), (PC_IP, RTT_PORT))

                # receive echo
                data, _ = self.sock.recvfrom(4096)
                t1 = time.time()

                resp = json.loads(data.decode())

                if resp["seq"] == self.seq:
                    rtt = (t1 - resp["t"]) * 1000

                    # send RTT value to receiver
                    msg = {
                        "type": "rtt_value",
                        "rtt": rtt
                    }

                    self.sock.sendto(json.dumps(msg).encode(), (PC_IP, RTT_PORT))

            except socket.timeout:
                pass

            time.sleep(0.5)

# ================= BRIDGE =================
class Bridge(Node):

    def __init__(self):
        super().__init__("ros2_srt_bridge")

        self.bridge = CvBridge()

        pipeline = (
            "appsrc ! videoconvert ! "
            "x264enc tune=zerolatency bitrate=2000 speed-preset=ultrafast ! "
            "mpegtsmux ! "
            f"srtsink uri=srt://{PC_IP}:{SRT_PORT}?mode=caller&passphrase={PASS}&pbkeylen=32"
        )

        self.writer = cv2.VideoWriter(
            pipeline,
            cv2.CAP_GSTREAMER,
            0,
            FPS,
            (WIDTH, HEIGHT),
            True
        )

        self.subscription = self.create_subscription(
            Image,
            "/image_raw",
            self.callback,
            10
        )

        print("Bridge started")

    def callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        self.writer.write(frame)

# ================= MAIN =================
def main():
    rclpy.init()

    # start RTT
    rtt = RTTClient()
    rtt.start()

    node = Bridge()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
