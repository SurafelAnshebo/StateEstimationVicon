import socket
import time
from vicon_dssdk import ViconDataStream

# Vicon setup
client = ViconDataStream.Client()
client.Connect("localhost:801")
client.EnableSegmentData()
client.SetBufferSize(1)
client.SetStreamMode(ViconDataStream.Client.StreamMode.EServerPush)
client.SetAxisMapping(
    ViconDataStream.Client.AxisMapping.EForward,
    ViconDataStream.Client.AxisMapping.ELeft,
    ViconDataStream.Client.AxisMapping.EUp
)

# Socket setup
HOST = '10.1.10.7'  # Ubuntu VM's IP address
PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
print(f"Connected to {HOST}:{PORT}")

subjectName = "S500"

try:
    while True:
        client.GetFrame()
        segmentName = client.GetSegmentNames(subjectName)[0]

        pos_data = client.GetSegmentGlobalTranslation(subjectName, segmentName)
        rot_data = client.GetSegmentGlobalRotationMatrix(subjectName, segmentName)

        if not (pos_data[1] or rot_data[1]):  # not occluded
            P = pos_data[0]
            R = rot_data[0]

            # Format pose as CSV string
            pose_str = f"{P[0]:.2f},{P[1]:.2f},{P[2]:.2f}," \
                       f"{R[0][0]:.4f},{R[0][1]:.4f},{R[0][2]:.4f}," \
                       f"{R[1][0]:.4f},{R[1][1]:.4f},{R[1][2]:.4f}," \
                       f"{R[2][0]:.4f},{R[2][1]:.4f},{R[2][2]:.4f}"

            sock.sendall(pose_str.encode('utf-8'))
            print("Sent:", pose_str)
        else:
            print("S500 is occluded.")

        time.sleep(2)

except KeyboardInterrupt:
    print("Stopping sender...")
finally:
    sock.close()
    client.Disconnect()
