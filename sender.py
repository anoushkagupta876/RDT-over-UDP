import sys
import time
import argparse
import socket
import select

from packet import Packet
def range_check(a, b, c):
   a %= 32
   b %= 32
   c %= 32
   # Either a is between (b, c] or a is either in (b, 31] or [0, c]
   return ((b < c) and (b < a <= c)) or ( (b < a <= 31) or ( 0 <= a <= c))

def logging(file, current_time, para):
   file.write(f"t={current_time} {para}\n")

def transmit_and_log(packet, current_time):
    """
    Logs the seqnum and transmits the packet through send_sock.
    """
    if packet.typ == 3:
      logging(seqnum_file, -1, 'SYN')
    elif packet.typ == 2:
       logging(seqnum_file, current_time, 'EOT')
    elif packet.typ == 1:
       current_time += 1
       logging(seqnum_file, current_time, packet.seqnum)
       
    send_socket.sendto(packet.encode(), (ne_host, int(ne_port)))

    return current_time
    
if __name__ == '__main__':
    # Parse args
    parser = argparse.ArgumentParser()
    parser.add_argument("ne_host", type=str, help="Host address of the network emulator")
    parser.add_argument("ne_port", type=int, help="UDP port number for the network emulator to receive data")
    parser.add_argument("port", type=int, help="UDP port for receiving ACKs from the network emulator")
    parser.add_argument("timeout", type=float, help="Sender timeout in milliseconds")
    parser.add_argument("filename", type=str, help="Name of file to transfer")
    args = parser.parse_args()

    with open(args.filename, 'r') as send_file, open('seqnum.log', 'w') as seqnum_file, \
          open('ack.log', 'w') as ack_file, open('N.log', 'w') as n_file, \
          socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as send_socket:
      
      current_time = 0
      window_size = 1

      ne_host = args.ne_host
      ne_port = args.ne_port
      port = args.port
      timeout = args.timeout

      timeout /= 1000

      timer = None

      window = {}

      # Setup UDP
      send_socket.bind(('', int(port)))

      # Handshake
      ack_received = False
      while ack_received is False:

        syn_packet = Packet(3, 0, 0, '')
        print('Syn packet sent')
        current_time = transmit_and_log(syn_packet, current_time)

        send_socket.settimeout(3)
        try: 
          recv_packet = send_socket.recvfrom(1024)
          ack_packet = Packet(recv_packet[0])

          if ack_packet.typ == 3 and ack_packet.seqnum == 0:
            print("Ack Received")
            print("Handshake Completed")
            ack_received = True
            send_socket.settimeout(None)

            logging(ack_file, -1, 'SYN')

            break
        except KeyboardInterrupt:
          print("Keyboard Interrupt - Ctrl + C - pressed by user")
          exit(0)
        except:
          continue
      
      logging(n_file, current_time, window_size)

      # Data Transmission
      seqnum = 0
      count_unacked = 0

      data = send_file.read(500)
      print('Data', data)

      while True:

        # print("Beginning Data Transmission")
        # EOT 
        if data == '':
          # Checks if all packets have been acked
          if count_unacked == 0:
           print('EOT Ready')
           break
          else:
             send_socket.settimeout(None)
        # if there is space in the window
        if count_unacked < window_size and data != None:
            # Sends a new packet
            data_packet = Packet(1, seqnum, len(data), data)
            current_time = transmit_and_log(data_packet, current_time)
            print("Data Send:", seqnum)

            # Adds that packet to the window
            window[seqnum] = data_packet

            # Updates the parameters 
            seqnum  = (seqnum + 1) % 32
            count_unacked += 1

            if timer == None:
              timer = time.time()

            # Reads the next set of data
            data = send_file.read(500)
            print(data)

        # Timeout
        if timer and time.time() - timer > timeout:
           print("Enter re-transmission")
           window_size = 1
           loss_seqnum = (seqnum - count_unacked)%32
           loss_packet = window[loss_seqnum]

           current_time = transmit_and_log(loss_packet, current_time)

           logging(n_file, current_time, window_size)

           timer = time.time()
        #---------------------------------------------------

        # Checks if there is anything which can received from the socket
        # Since time is 0.0, it will not block
        ready = select.select([send_socket], [], [], 0.0)
        send_socket.settimeout(0)
        ready = select.select([send_socket], [], [], 0.0)
        # print(ready)
        if ready[0]:
          recv_packet = send_socket.recvfrom(2048)
          ack_packet = Packet(recv_packet[0])
          print("ACK is here")
          # ACK
          if ack_packet.typ == 0:
              
              print("Received Packet ACK")
              current_time += 1
              logging(ack_file, current_time, ack_packet.seqnum)

              if range_check(ack_packet.seqnum, seqnum - count_unacked, seqnum):
                  print("Enter range check")
                  # Cumulative ACKS
                  count_unacked -= ack_packet.seqnum - (seqnum - count_unacked) + 1
                  
                  if count_unacked > 0:
                    timer = time.time()
                  else:
                    timer = None
                  
                  if window_size < 10:
                    window_size += 1 
                    logging(n_file, current_time, window_size)
        if recv_packet == None:
          print("NO ACK Available")
          # continue
          
      # EOT 
      send_socket.settimeout(3)
      eot_ack_received = False

      current_time += 1
      while eot_ack_received is False:

        eot_packet = Packet(2, seqnum, 0, '')
        print('EOT Send')
        transmit_and_log(eot_packet, current_time)
        print(current_time)
        try: 
          recv_packet = send_socket.recvfrom(1024)
          eot_packet = Packet(recv_packet[0])
          if eot_packet.typ == 2:
            current_time += 1
            logging(ack_file, current_time, 'EOT')
            print("EOT ACK Received")
            eot_ack_received = True
            send_socket.settimeout(None)
            send_socket.close()
            break
          # else:
          #   print("Incorrect type of ACK - Expected EOT")
          #   exit(1)
            # logging(ack_file, -1, 'SYN')
        except KeyboardInterrupt:
          print("Keyboard Interrupt - Ctrl + C - pressed by user")
          exit(0)
        except:
          continue




         
        
