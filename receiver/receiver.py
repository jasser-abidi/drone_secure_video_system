import cv2
import time
from datetime import datetime
import collections
import socket
import json
import threading

PORT = 9000
RTT_PORT = 9001
PASS = "PFE_secure_2026"


CODEC = "H264"

# ================= RTT METRICS =================
class RTTMetrics:
    def __init__(self):
        self.history = collections.deque(maxlen=20)
        self.last = 0
        self.avg = 0
        self.jitter = 0

    def update(self, rtt):
        prev = self.history[-1] if self.history else rtt
        self.history.append(rtt)

        self.last = rtt
        self.avg = sum(self.history) / len(self.history)
        self.jitter = abs(rtt - prev)

    def latency(self):
        return self.avg / 2

# ================= RTT SERVER =================
class RTTServer(threading.Thread):
    def __init__(self, metrics):
        super().__init__(daemon=True)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", RTT_PORT))
        self.metrics = metrics

    def run(self):
        while True:
            data, addr = self.sock.recvfrom(4096)
            packet = json.loads(data.decode())

            if packet.get("type") == "rtt_probe":
                self.sock.sendto(data, addr)

            elif packet.get("type") == "rtt_value":
                self.metrics.update(packet["rtt"])

# ================= PIPELINE =================
pipeline = (
    f"srtsrc uri=srt://:{PORT}?mode=listener&passphrase={PASS}&pbkeylen=32 latency=50 ! "
    "queue ! tsdemux ! h264parse ! avdec_h264 ! videoconvert ! appsink drop=1 sync=false"
)

cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("Erreur ouverture flux")
    exit()

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480

filename = "drone_record_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".avi"
fourcc = cv2.VideoWriter_fourcc(*"XVID")

out = cv2.VideoWriter(filename, fourcc, 15, (width, height))

print("Receiver started")

metrics = RTTMetrics()
RTTServer(metrics).start()

prev_time = time.time()
frame_count = 0
lost_frames = 0
fps_history = collections.deque(maxlen=60)

font = cv2.FONT_HERSHEY_SIMPLEX

while True:

    ret, frame = cap.read()

    if not ret:
        lost_frames += 1
        continue

    frame_count += 1

    now = time.time()
    fps = 1/(now-prev_time) if now != prev_time else 0
    prev_time = now

    fps_history.append(fps)

    total = frame_count + lost_frames
    packet_loss = (lost_frames/total)*100 if total > 0 else 0

    # ===== RTT VALUES =====
    rtt = metrics.last
    latency = metrics.latency()
    jitter = metrics.jitter

    resolution = f"{width}x{height}"

    # ===== HUD =====
    cv2.rectangle(frame,(10,10),(270,200),(0,0,0),-1)
    cv2.rectangle(frame,(10,10),(270,200),(255,255,255),1)

    x, y = 20, 35
    step = 22

    cv2.putText(frame,"Drone Video System",(x,y),font,0.6,(0,255,255),2)

    y += step
    cv2.putText(frame,f"Resolution : {resolution}",(x,y),font,0.5,(255,255,255),1)

    y += step
    cv2.putText(frame,f"FPS : {fps:.2f}",(x,y),font,0.5,(255,255,255),1)

    y += step
    cv2.putText(frame,f"RTT : {rtt:.1f} ms",(x,y),font,0.5,(0,255,0),1)

    y += step
    cv2.putText(frame,f"Latency : {latency:.1f} ms",(x,y),font,0.5,(0,255,0),1)

    y += step
    cv2.putText(frame,f"Jitter : {jitter:.1f} ms",(x,y),font,0.5,(0,255,0),1)

    y += step
    cv2.putText(frame,f"Packet Loss : {packet_loss:.2f} %",(x,y),font,0.5,(255,255,255),1)

    y += step
    cv2.putText(frame,f"Codec : {CODEC}",(x,y),
            font,0.5,(255,255,255),1)

    y += step
    cv2.putText(frame,"Encryption : AES256",(x,y),
            font,0.5,(0,200,255),1)

    cx = width // 2
    cy = height // 2

    size = 15

    # horizontal
    cv2.line(frame,(cx-size,cy),(cx+size,cy),(0,255,0),2)

    # vertical
    cv2.line(frame,(cx,cy-size),(cx,cy+size),(0,255,0),2)


    cv2.imshow("Drone Live",frame)
    out.write(frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
out.release()
cv2.destroyAllWindows()

print("Video saved :", filename)
