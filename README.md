# mongol
A MongoDB no authentication scanner and enumerator

MongoDB runs without authentication unless its enabled .
This tool scans a network for open MongoDB ports and tries to connect without authentication and enumerates all databases and collection .

```
usage : mongol.py -l -o
```
<b>Flags:</b>
```
  [-l] [-log] - logs exceptions into log.txt file
  [-o] [--output] - outputs successful enumerations into a file
```

<b>Requirements:</b>
```
nmap
pymongo
```
<b>Todo :</b>
- Prettify the output being saved into output.txt
- Add argparse for cidr list file path
- Add argparse for single network scan , for example : "192.168.0.1/24"
- Add logic so the script will know how to choose a network to scan - from file or from argparse
