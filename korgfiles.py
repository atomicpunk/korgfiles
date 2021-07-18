#!/usr/bin/env python3
#
# Copyright 2021 Todd Brandt <todd.eric.brandt@gmail.com>
#
# Korg File Utility
#
# Supports commands related to KORG file ma management
#
# extract
# Extract korg sng, pcg, ksc, ksf, and kmp files from any disk image.
# The files can even be deleted as the tool does not look at the file
# allocation tables, it scans the whole memory of the image.
#
# ksf2wav
# Convert KORG Sound Files to WAV format
#

import sys
import os
import string
import struct
import re
import argparse
import mmap

def doError(msg, fatal=True):
	print('ERROR: %s' % msg)
	if fatal:
		sys.exit(1)

def unused_file_name(name, ext):
	maxdups = 10000
	file = ''
	for i in range(1, maxdups + 2):
		if i > maxdups:
			return ''
		file = (name if i == 1 else ('%s%d' % (name, i))) + ext
		if not os.path.exists(file):
			break
	return file

def extract_sng_file(data, start):
	name = data[start+0x70:start+0x80]
	if not name.isascii():
		return False
	name = (' '.join(name.decode().strip().split())).replace(' ', '_')
	b1, b2, b3 = struct.unpack('xBBB', data[start+0x6c:start+0x70])
	size = (b1 * 0x10000) + (b2 * 0x100) + b3 - 93476
	file = unused_file_name(name, '.SNG')
	if not file:
		return False
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
	file = unused_file_name(name, '.PCG')
	if not file:
		return False
	fp = open(file, 'wb')
	fp.write(data[start:start+size])
	fp.close()
	print('%s: %d bytes' % (file, size))
	return True

def extract_ksf_file(data, start):
	name = data[start+0x8:start+0x18]
	if not name.isascii():
		return False
	suffix = '.KSF'
	name = (' '.join(name.decode().strip().split())).replace(' ', '_')
	if name.upper().endswith('.KSF'):
		name = name[0:-4]
	b1, b2 = struct.unpack('>II', data[start+0x20:start+0x28])
	size = b1 + b2 + 0x42
	# try to salvage any damaged ksf snippets
	for tgt in [b'KORG', b'SMP1', b'MSP1']:
		match = re.search(tgt, data[start+0x30:start+size])
		if match and match.start() + 0x30 < size:
			size = match.start() + 0x30
			suffix = '-DMG.KSF'
	file = unused_file_name(name, suffix)
	if not file:
		return False
	fp = open(file, 'wb')
	fp.write(data[start:start+size])
	fp.close()
	if 'DMG' in suffix:
		print('%s (damaged): %d bytes' % (file, size))
	else:
		print('%s: %d bytes' % (file, size))
	return True

def extract_kmp_file(data, start):
	maxbytes = 100000
	name = data[start+0x8:start+0x18]
	if not name.isascii():
		return False
	name = (' '.join(name.decode().strip().split())).replace(' ', '_')
	if name.upper().endswith('.KMP'):
		name = name[0:-4]
	end = start + maxbytes if start + maxbytes < len(data) else len(data)
	match = re.search(b'\x00\x00\x00\x00', data[start:end])
	if not match:
		return False
	size = match.start()
	file = unused_file_name(name, '.KMP')
	if not file:
		return False
	fp = open(file, 'wb')
	fp.write(data[start:start+size])
	fp.close()
	print('%s: %d bytes' % (file, size))
	return True

def extract_ksc_file(data, start):
	maxbytes = 100000
	for sz in range(0, maxbytes + 2):
		if sz > maxbytes:
			return False
		if not data[start+sz:start+sz+1].isascii() or data[start+sz] == 0:
			break
	name = 'KORG'
	file = unused_file_name(name, '.KSC')
	if not file:
		return False
	fp = open(file, 'wb')
	fp.write(data[start:start+sz])
	fp.close()
	print('%s: %d bytes' % (file, sz))
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
		elif tgt == 'kmp':
			extract_kmp_file(data, match.start())
		elif tgt == 'ksc':
			extract_ksc_file(data, match.start())
		else:
			extract_unknown_file(data, match.start())
	fp.close()

def ksf2wav(file, args):
	# read in the ksf file data
	fp = open(file, 'rb')
	data = fp.read()
	fp.close()

	# check file size
	filesize = len(data)
	if filesize < 74:
		doError('%s is not large enough to be usable (%d bytes)' % \
			(file, filesize), False)
		return False

	# verify this is a ksf file
	h1, h2 = data[0:4].decode(), data[40:44].decode()
	if h1 != 'SMP1' or h2 != 'SMD1':
		doError('%s is not a korg sample file (KSF)' % file, False)
		return False

	# extract size data and verify enough data exists
	samples, val1, fsize, rate, val2, val3 = struct.unpack('>IIxxxxIIII',
		data[32:60])
	if (filesize - 60) < (samples * 2) or rate > 200000:
		doError('ksf file %s is corrupt' % file, False)
		return False

	# determine the name & size of the output wav file
	name = data[7:24].decode().strip()
	if args.keepname or not name:
		name = os.path.basename(file).upper().replace('.KSF', '')
	else:
		name = (' '.join(name.split())).replace(' ', '_')
	wavfile = unused_file_name(name, '.WAV')
	if not wavfile:
		doError('could not find an unused wav file name for %s' % file, False)
		return False
	wavsize = (samples * 2) + 44

	print('KSF IN : %s (%d bytes)' % (os.path.basename(file), filesize))
	print('WAV OUT: %s (%d bytes)' % (wavfile, wavsize))

	# write the WAV format header
	header = struct.pack('<4sI8sIHHIIHH4sI', b'RIFF', wavsize - 8, b'WAVEfmt ',
		0x10, 1, 1, rate, rate * 2, 2, 0x10, b'data', wavsize - 44)
	fp = open(wavfile, 'wb')
	fp.write(header)

	# write the WAV sound data
	for c in range(samples):
		i = (c * 2) + 60
		sample = struct.unpack('>H', data[i:i+2])[0]
		fp.write(struct.pack('<H', sample))
	fp.close()
	return True

if __name__ == '__main__':
	import argparse

	parser = argparse.ArgumentParser()
	subparse = parser.add_subparsers(help='command to run')

	parse1 = subparse.add_parser('extract', help='extract korg files from a disk image')
	parse1.add_argument('diskimage',
		help='image file with partition data in it')
	parse1.add_argument('filetype', choices=['sng', 'pcg', 'ksc', 'ksf', 'kmp'],
		help='korg filetype to extract')

	parse2 = subparse.add_parser('ksf2wav', help='convert a ksf sound file to wav')
	parse2.add_argument('ksffile', nargs='+',
		help='ksf sound file(s) to convert to wav(s)')
	parse2.add_argument('-keepname', action='store_true',
		help='keep the ksf filename as the wav filename')

	args = parser.parse_args()
	vlist = vars(args)

	if 'diskimage' in vlist:
		if not os.path.exists(args.diskimage):
			doError('file does not exist - %s' % args.diskimage)
		find_in_file(args.diskimage, args.filetype)
	elif 'ksffile' in vlist:
		for file in args.ksffile:
			if not os.path.exists(file):
				doError('file does not exist - %s' % file, False)
			ksf2wav(file, args)
	else:
		parser.print_help()
		sys.exit(1)
