import pandas as pd

from scapy.all import *
from scapy.layers.inet import IP, TCP

t00 = time.mktime((2017, 7, 5, 9, 47, 0, 0, 0, -1))
t01 = time.mktime((2017, 7, 5, 10, 11, 0, 0, 0, -1))
t10 = time.mktime((2017, 7, 5, 10, 14, 0, 0, 0, -1))
t11 = time.mktime((2017, 7, 5, 10, 36, 0, 0, 0, -1))
t20 = time.mktime((2017, 7, 5, 10, 43, 0, 0, 0, -1))
t21 = time.mktime((2017, 7, 5, 11, 1, 0, 0, 0, -1))
t30 = time.mktime((2017, 7, 5, 11, 10, 0, 0, 0, -1))
t31 = time.mktime((2017, 7, 5, 11, 24, 0, 0, 0, -1))

rows = {}
dos = 'A'
pckNum = 0

while True:
    with PcapReader('exemplo.pcap') as packets:
        for packet in packets:

            pckNum = pckNum + 1

            if TCP in packet and IP in packet:

                if pckNum % 1000 == 0:
                    print(pckNum, len(rows.keys()), datetime.fromtimestamp(packet.time).strftime('%Y-%m-%d %H:%M:%S.%f'),
                          t00 - packet.time)

                # Cria o registro de abertura da conexao
                if packet[TCP].flags == 'S':  # SYN (abrindo a conexao)
                    # print(pckNum, datetime.fromtimestamp(packet.time).strftime('%Y-%m-%d %H:%M:%S.%f'))
                    # print(ls(packet))

                    key = '{}:{}:{}-{}:{}:{}'.format(packet.src, packet[IP].src, packet[TCP].sport,
                                                     packet.dst, packet[IP].dst, packet[TCP].dport)
                    if key not in rows:
                        newRow = [packet.time,  # 0 'Timestamp'
                                  packet[IP].src,  # 1 'SourceIP'
                                  packet[IP].dst,  # 2 'DestinationIP'
                                  packet[TCP].sport,  # 3 'SourcePort'
                                  packet[TCP].dport,  # 4 'DestinationPort'
                                  0,  # 5 'FirstAckTimestamp'
                                  3600,  # 6 'FinTimestamp' = 1h  (60sec * 60min)
                                  packet[IP].len - 40,  # 7 'TotalLength'
                                  0,  # 8 'PacketsFromServer'
                                  -1000]  # 9 'PacketsPerTotalTime'
                        rows[key] = newRow
                        continue
                # end if ( packet[TCP].flags == 'S' ):

                # pacote com ACK
                if packet[TCP].flags == 'A':
                    # ACK
                    # agora verifica salva o tempo do primeiro ACK
                    key = '{}:{}:{}-{}:{}:{}'.format(packet.src, packet[IP].src, packet[TCP].sport
                                                     , packet.dst, packet[IP].dst, packet[TCP].dport)
                    if key in rows:
                        row = rows[key]
                        # salva o intervalo entre o SYN e o primeiro ACK
                        if row[5] == 0:
                            row[5] = packet.time - row[0]  # 5 'FirstAckTimestamp'
                            row[7] = row[7] + packet[IP].len - 40  # 7 'TotalLength'
                            row[8] = row[8] + 1  # 8 'PacketsFromServer'
                            rows[key] = row
                            continue
                        else:  # continua contanto o tamanho dos pacotes
                            row[7] = row[7] + packet[IP].len - 40  # 7 'TotalLength'
                            row[8] = row[8] + 1  # 8 'PacketsFromServer'
                            rows[key] = row
                            continue
                # end if (packet[TCP].flags == 'A'):

                # pacote com FIN
                if packet[TCP].flags == 'F' or packet[TCP].flags == 'FA' or packet[TCP].flags == 'FPA':
                    # FIN - Cliente encerrando
                    key = '{}:{}:{}-{}:{}:{}'.format(packet.src, packet[IP].src, packet[TCP].sport
                                                     , packet.dst, packet[IP].dst, packet[TCP].dport)
                    if key in rows:
                        row = rows[key]
                        # salva o intervalo entre o SYN e o FIN
                        row[6] = packet.time - row[0]  # 6 'FinTimestamp'
                        row[7] = row[7] + packet[IP].len - 40  # 7 'TotalLength'
                        row[8] = row[8] + 1  # 8 'PacketsFromServer'
                        if row[8] > 1:
                            row[9] = row[8] / row[6]  # 9 'PacketsPerTotalTime'
                        rows[key] = row
                        continue

                    # FIN - Servidor encerrando
                    key = '{}:{}:{}-{}:{}:{}'.format(packet.dst, packet[IP].dst, packet[TCP].dport
                                                     , packet.src, packet[IP].src, packet[TCP].sport)
                    if key in rows:
                        row = rows[key]
                        # salva o intervalo entre o SYN e o FIN
                        row[6] = packet.time - row[0]  # 6 'FinTimestamp'
                        row[7] = row[7] + packet[IP].len - 40  # 7 'TotalLength'
                        row[8] = row[8] + 1  # 8 'PacketsFromServer'
                        if row[8] > 1:
                            row[9] = row[8] / row[6]  # 9 'PacketsPerTotalTime'
                        rows[key] = row

                # end if (packet[TCP].flags == 'F'):

            # end if(TCP in packet):

        # end for
    # end with

    # salva o dataframe, em csv
    df = pd.DataFrame(rows.values())
    df.to_csv('newAccess.csv', index=False, header=False)
