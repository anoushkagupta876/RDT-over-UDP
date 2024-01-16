import os
import sys
import argparse
import socket
import math

from packet import Packet

# Writes the received content to file
def append_to_file(filename, data):
    file = open(filename, 'a')
    file.write(data)
    file.close()

def append_to_log(packet):
    """
    Appends the packet information to the log file
    """
    log_filename = 'arrival.log'
    if packet.typ == 3:
        print("SYN send")
        append_to_file(log_filename, 'SYN\n')
    elif packet.typ == 2:
        print("EOT send")
        append_to_file(log_filename, 'EOT\n')
    elif packet.typ == 0:
        print("Packet send: ", packet.seqnum)
        append_to_file(log_filename, str(packet.seqnum)+ '\n')

    

def send_ack(typ, seqnum, length = 0, data = ''): #Args to be added
    """
    Sends ACKs, EOTs, and SYN to the network emulator. and logs the seqnum.
    """
    packet = Packet(typ, seqnum, length, data)
    append_to_log(packet)
    s.sendto(packet.encode(), 
             (args.ne_addr, int(args.ne_port)))
    

    
if __name__ == '__main__':
    # Parse args
    parser = argparse.ArgumentParser(description="Congestion Controlled GBN Receiver")
    parser.add_argument("ne_addr", metavar="<NE hostname>", help="network emulator's network address")
    parser.add_argument("ne_port", metavar="<NE port number>", help="network emulator's UDP port number")
    parser.add_argument("recv_port", metavar="<Receiver port number>", help="network emulator's network address")
    parser.add_argument("dest_filename", metavar="<Destination Filename>", help="Filename to store received data")
    args = parser.parse_args()

    # Clear the output and log files
    open(args.dest_filename, 'w').close()
    open('arrival.log', 'w').close()

    expected_seq_num = 0 # Current Expected sequence number
    seq_size = 32 # Max sequence number
    max_window_size = 10 # Max number of packets to buffer
    recv_buffer = {}  # Buffer to store the received data

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:

        s.bind(('', int(args.recv_port))) 
        # Socket to receive data
       
        while True:
            # Receive packets, log the seqnum, and send response
            
            recv_packet, addr = s.recvfrom(2048)
            data_packet = Packet(recv_packet)

            # SYN packet
            if data_packet.typ == 3 and data_packet.seqnum == 0:
                send_ack(3, 0)

            elif data_packet.seqnum == expected_seq_num:
                if data_packet.typ == 2:
                    print("EOT Received")
                    send_ack(2, 0)
                    break
                else:
                    print("Enter expected = current")
                    append_to_file(args.dest_filename, data_packet.data)
                    curr_seqnum = (data_packet.seqnum 
                    + 1) % seq_size

                    while curr_seqnum in recv_buffer:
                        append_to_file(args.dest_filename, recv_buffer[curr_seqnum].data)
                        recv_buffer.pop(curr_seqnum)
                        curr_seqnum = (curr_seqnum 
                    + 1) % seq_size 
                        
                    send_ack(0, (curr_seqnum - 1) % seq_size)

                    expected_seq_num = curr_seqnum

            else:
                if data_packet.seqnum > expected_seq_num and data_packet.seqnum  <= (expected_seq_num + 10) % seq_size:
                    recv_buffer[data_packet.seqnum] = data_packet
                
                send_ack(0, (expected_seq_num - 1) % seq_size)



                    