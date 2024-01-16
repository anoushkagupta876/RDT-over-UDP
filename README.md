# Congestion Controlled Pipelined RDT over UDP

## Project Overview
This project implements a congestion-controlled pipelined Reliable Data Transfer (RDT) protocol over UDP to transfer text files across an unreliable network. The protocol is designed to handle packet loss, reordering, and duplicates, ensuring reliable data transmission from a sender to a receiver.

## Components
1. **Sender Program**: Initiates the file transfer, handles congestion control, and sends packets through the network emulator.
2. **Receiver Program**: Receives data packets, sends acknowledgments, and writes the received data into an output file.
3. **Network Emulator**: Simulates an unreliable network by introducing packet loss, reordering, and duplicates.

## Packet Format
Packets are structured with integer fields for type (0: ACK, 1: Data, 2: EOT, 3: SYN), sequence number (modulo 32), and length, followed by the data string (max 500 characters).

## Implementation
- **Connection Establishment**: SYN packets are used to establish a connection.
- **Data Transmission**: Data is read from a file and sent using the RDT protocol. Window-based congestion control is implemented with a starting window size of 1, incrementing up to a maximum of 10.
- **Connection Termination**: EOT packets are used to terminate the connection.

## Logging
- `seqnum.log`: Logs sequence numbers of sent packets.
- `ack.log`: Logs sequence numbers of received ACK packets.
- `N.log`: Logs changes in the window size.

## Receiver Output
- `arrival.log`: Logs sequence numbers of all received data packets.

## Running the Programs
### Network Emulator
```bash
python network_emulator.py <forward_port> <receiver_address> <receiver_port> <backward_port> <sender_address> <sender_port> <max_delay> <discard_probability> <verbose_mode>
```
### Sender
```bash
python sender.py <emulator_host> <emulator_port> <ack_port> <timeout_interval> <file_to_transfer>
```

### Receiver
```bash
python receiver.py <emulator_host> <emulator_ack_port> <data_port> <output_file>
```


