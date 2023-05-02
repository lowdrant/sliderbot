#!/usr/bin/env python3
from argparse import ArgumentParser
from serial import Serial,SerialException
from time import time,sleep


parser = ArgumentParser('Log serial data from serial')
parser.add_argument('fn',help='log filename')
parser.add_argument('--tty', default=None,help='serial port filename')
parser.add_argument('--tf', default=10,type=float,help='logger runtime (seconds)')
parser.add_argument('--baud',type=int,default=1000000,help='baudrate')

if __name__=='__main__':
    # Arg Parse
    args=parser.parse_args()
    tf = args.tf
    if args.tty is not None:
        ser = Serial(args.tty, args.baud)
    else:
        for i in range(4):
            try:
                ser = Serial(f'/dev/ttyACM{i}',args.baud)
            except SerialException:
                pass
            else:
                break

    # Clear Buffer
    print('Clearing buffer...')
    ser.read(ser.in_waiting)
    ser.read(ser.in_waiting)

    # Read and Dump
    print(f'Reading from {ser.port} at {ser.baudrate} baud for {tf} seconds to {args.fn}')
    f = open(args.fn,'w')
    ser.read(ser.in_waiting)
    tr = time()
    try:
        while (time() - tr < tf):
            f.write(ser.readline().decode())
    finally:
        f.close()
        print('Done!')