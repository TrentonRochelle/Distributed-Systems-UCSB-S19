#!/bin/sh
python3 ledger.py
python3 server.py 5010 &
python3 client.py Alice 5000