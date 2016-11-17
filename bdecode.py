import sys
from pprint import pprint
from better_bencode import _pure as bencode

d = bencode.load(open(sys.argv[1], "rb"))
if b'info' in d and b'pieces' in d[b'info']:
	d[b'info'][b'pieces'] = "(...)"
pprint(d)
