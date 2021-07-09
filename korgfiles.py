#!/usr/bin/env python3
#
# Copyright 2021 Todd Brandt <todd.eric.brandt@gmail.com>
#
# Korg File Extractor
#
# Extract korg sng, pcg, ksc, ksf, and kmp files from any disk image
# or device. The files can even be deleted as the tool does not look
# at the file allocation tables, it scans the whole memory of the image.
#

import sys
import os
import string
import struct
import re
import argparse
import mmap

def extract_sng_file(data, start):
	name = data[start+0x70:start+0x80]
	if not name.isascii():
		return False
	name = (' '.join(name.decode().strip().split())).replace(' ', '_')
	b1, b2, b3 = struct.unpack('xBBB', data[start+0x6c:start+0x70])
	size = (b1 * 0x10000) + (b2 * 0x100) + b3 - 93476
	for i in range(1, 1002):
		if i > 1000:
			return False
		file = (name if i == 1 else ('%s%d' % (name, i))) + '.SNG'
		if not os.path.exists(file):
			break
	fp = open(file, 'wb')
	fp.write(data[start:start+size])
	fp.close()
	print('%s: %d bytes' % (file, size))
	return True

def extract_pcg_file(data, start):
	b1, b2, b3, b4, b5, b6 = struct.unpack('>IxxxxIxxxxIxxxxIxxxxIxxxxI',
		data[start+0x24:start+0x50])
	name = 'KORG'
	size = b1 + b2 + b3 + b4 + b5 + b6 + 0x50
	if size > 1000000:
		return False
	for i in range(1, 1002):
		if i > 1000:
			return False
		file = (name if i == 1 else ('%s%d' % (name, i))) + '.PCG'
		if not os.path.exists(file):
			break
	fp = open(file, 'wb')
	fp.write(data[start:start+size])
	fp.close()
	print('%s: %d bytes' % (file, size))
	return True

def extract_ksf_file(data, start):
	name = data[start+0x8:start+0x18]
	if not name.isascii():
		return False
	name = (' '.join(name.decode().strip().split())).replace(' ', '_')
	if name.upper().endswith('.KSF'):
		name = name[0:-4]
	b1, b2 = struct.unpack('>II', data[start+0x20:start+0x28])
	size = b1 + b2 + 0x42
	for i in range(1, 1002):
		if i > 1000:
			return False
		file = (name if i == 1 else ('%s%d' % (name, i))) + '.KSF'
		if not os.path.exists(file):
			break
	fp = open(file, 'wb')
	fp.write(data[start:start+size])
	fp.close()
	print('%s: %d bytes' % (file, size))
	return True

def extract_unknown_file(data, start):
	print('%11d: %s' % (start, data[start:start+100]))
	return False

def find_in_file(file, tgt):
	fmtstring = {
		'sng': b'KORG;\x01\x01',
		'pcg': b'KORG;\x00\x00',
		'ksc': b'#KORG Script',
		'ksf': b'SMP1\x00\x00\x00\x20',
		'kmp': b'MSP1\x00\x00\x00\x12',
	}
	target = fmtstring[tgt] if tgt in fmtstring else tgt.encode('ascii')

	fp = open(file, 'rb')
	data = mmap.mmap(fp.fileno(), 0, access=mmap.ACCESS_READ)
	list = re.finditer(target, data)
	for match in list:
		if tgt == 'sng':
			extract_sng_file(data, match.start())
		elif tgt == 'pcg':
			extract_pcg_file(data, match.start())
		elif tgt == 'ksf':
			extract_ksf_file(data, match.start())
		else:
			extract_unknown_file(data, match.start())
	fp.close()

if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser()
	parser.add_argument('diskimage',
		help='image file or device with partition data in it')
	parser.add_argument('filetype', choices=['sng', 'pcg', 'ksc', 'ksf', 'kmp'],
		help='korg filetype to extract')
	args = parser.parse_args()

	find_in_file(args.diskimage, args.filetype)
