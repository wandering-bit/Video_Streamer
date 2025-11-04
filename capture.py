import cv2
import socket
import os

cam = cv2.VideoCapture(0)

chunk_size = 900
s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0",10000))
s.settimeout(10.0)
sequence_number = 0
while True:
    if sequence_number == 253:
        sequence_number=0
    id = 1
    ret, frame = cam.read()
    if not(ret):
        continue
    _,encoded = cv2.imencode(".jpg",frame)
    byte_stream = encoded.tobytes()
    last =0
    chunks = int(len(byte_stream)/chunk_size)
    last_index = chunks*chunk_size
    remain = len(byte_stream)-last_index
    data_size = last_index+remain+(chunk_size-remain)
    for i in range(0,last_index,chunk_size):
        starting_index = i
        ending_index = i+chunk_size
        byte_id = id.to_bytes(2,byteorder="big")
        byte_data_size=data_size.to_bytes(4,byteorder="big")
        byte_sequence_number = sequence_number.to_bytes(1,byteorder="big")
        packet = byte_sequence_number+byte_id+byte_data_size+byte_stream[starting_index:ending_index]
        s.sendto(packet,("3.109.3.254",8000))
        id+=1

    byte_id = id.to_bytes(2,byteorder="big")
    byte_data_size=data_size.to_bytes(4,byteorder="big")
    byte_sequence_number = sequence_number.to_bytes(1,byteorder="big")
    last = byte_sequence_number+byte_id+byte_data_size+byte_stream[last_index:last_index+remain]
    s.sendto(last,("3.109.3.254",8000))
    sequence_number+=1

    if cv2.waitKey(1) == ord('q'):
        break 

cam.release()
cv2.destroyAllWindows()