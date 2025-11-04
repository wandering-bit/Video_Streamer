import socket
import time
import os
import cv2
import threading

handshake = "x4tKzQ7GHmY2sC8rJv234FE#FbwdfeeerwePdNaR0uT5asdfasBFdfewrVDFEFEVvasdwZ34fbi3WXqglOMpU9yE1hL6jDnBwFScVkAeHo"
connected_flag = False
s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.settimeout(10)
s.bind(("0.0.0.0",11000))
heartbeat=0
image_path = "D:/Personal/videoStreamer/output.jpg"
server_address = "3.109.3.254"

def send_heartbeat():
    while True:
        s.sendto(b'heartbeat',(server_address,8000))
        time.sleep(1)

t1 = threading.Thread(target=send_heartbeat,daemon=True)

t1.start()

while True:
    try:
        if connected_flag==False:
            while True:
                s.sendto(handshake.encode("utf-8"),(server_address,8000))
                data,addr = s.recvfrom(106)
                if data== b'hello':
                    connected_flag= True
                    break
                time.sleep(1)

        order_map={}
        bytes_read=0
        chunk_size = 900
        old_sequence=-1
        current_sequence = 0
        while True:
            buf,addr = s.recvfrom(907)
            current_sequence = buf[0]
            if current_sequence!=old_sequence and old_sequence>-1:
                order_map={}
                bytes_read=0
                
            current = int.from_bytes(buf[1:3],byteorder="big")
            data_size = int.from_bytes(buf[3:7],byteorder="big")
            order_map[current]=buf[7:]
            bytes_read = bytes_read+chunk_size
            end = int(data_size/chunk_size)
            if bytes_read==data_size:
                last_read_flag=0
                data = bytearray()
                for i in range(1,end+1):
                    if i not in order_map:
                        continue
                    for j in order_map[i]:
                        data.append(j)
                        if j==217 and data[len(data)-2]==255:
                            last_read_flag=1
                            break
                if last_read_flag!=1:
                    continue
                file = open(image_path,"wb")
                file.write(data)
                file.close()
                order_map={}
                bytes_read=0
                image = cv2.imread(image_path)
                cv2.imshow('image',image)
                if cv2.waitKey(1) == ord('q'):
                    break 
            old_sequence=current_sequence

    except KeyboardInterrupt:
        print("\nExiting...")
        s.close()

    except Exception as e:
        connected_flag=0