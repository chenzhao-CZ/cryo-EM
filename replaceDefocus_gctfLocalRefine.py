######################################################################################################################
# Chen Zhao
# czhao@rockefeller.edu
# replace defocus from values after Gctf local refine
# works for both relion 3.1 and relion 3-
# to run:
# python replaceDefocus_gctfLocalRefine.py particles-to-be-replaced.star new_name.star path-to-_local.star
# python replaceDefocus_gctfLocalRefine.py particles-to-be-replaced.star new_name.star path-to-_local.star --original
#		if imageOriginalName should be used
######################################################################################################################

import argparse
import os

def getDefocus(path):
	print 'getting defocus values from Gctf local refinement...'
	defocus = {}
	header = {}
	for filename in os.listdir(path):
		if filename.endswith('local.star'):
			num = int(eval(filename.split('/')[-1].split('_')[1].strip('0')))
			with open(path + filename) as star:
				readHeader = 0
				for line in star:
					# parse header
					if line.startswith('_rln'):
						readHeader = 1
						entry = line.split(' ')
						header[entry[0]] = eval(entry[1][1:]) - 1
					# parse entries
					elif line.strip() and readHeader:
						items = line[:-1].split()
						coord = ( num, int(eval(items[header['_rlnCoordinateX']])), int(eval(items[header['_rlnCoordinateY']])) )
						if coord not in defocus.keys():
							defocus[coord] = ( items[header['_rlnDefocusU']], items[header['_rlnDefocusV']], items[header['_rlnDefocusAngle']] )
						else:
							print 'Error! Duplicated entries that should never happen'
							exit()
	return defocus

def replaceDefocus(defocus, outfilename, particles, ori):
	print 'replacing defocus values in input particle.star...'
	with open(particles, 'r') as infile, open(outfilename, 'w') as outfile:
		for line in infile:
			outfile.write(line)
			if line.startswith('data_optics'):
				replaceRelion31(defocus, outfile, infile, ori)
			elif line.startswith('data_'):
				replaceRelion3(defocus, outfile, infile, ori)

def replaceRelion31(defocus, outfile, infile, ori):
	startParticles = 0
	header = {}
	readHeader = 0
	for line in infile:
		if not startParticles:
			outfile.write(line)
			if line.startswith('data_particles'):
				startParticles = 1
		else:
			if line.startswith('_rln'):
				readHeader = 1
				entry = line.split(' ')
				header[entry[0]] = eval(entry[1][1:]) - 1
				outfile.write(line)
			elif line.strip() and readHeader:
				items = line[:-1].split()
				if ori:
					num = int(eval(items[header['_rlnImageOriginalName']].split('/')[-1].split('.')[0].split('_')[1].strip('0')))
				else:
					num = int(eval(items[header['_rlnImageName']].split('/')[-1].split('.')[0].split('_')[1].strip('0')))
				try:
					( items[header['_rlnDefocusU']], items[header['_rlnDefocusV']], items[header['_rlnDefocusAngle']] ) = \
							defocus[ ( num, int(eval(items[header['_rlnCoordinateX']])), int(eval(items[header['_rlnCoordinateY']])) ) ]
					outfile.write(' \t'.join(items) + '\n')
				except KeyError:
					print 'Particle coordinates not found. Something went wrong...'
					exit()
			elif not readHeader:
				outfile.write(line)

def replaceRelion3(defocus, outfile, infile, ori):
	header = {}
	readHeader = 0
	for line in infile:
		if line.startswith('_rln'):
			readHeader = 1
			entry = line.split(' ')
			header[entry[0]] = eval(entry[1][1:]) - 1
			outfile.write(line)
		elif line.strip() and readHeader:
			items = line[:-1].split()
			if ori:
				num = int(eval(items[header['_rlnImageOriginalName']].split('/')[-1].split('.')[0].split('_')[1].strip('0')))
			else:
				num = int(eval(items[header['_rlnImageName']].split('/')[-1].split('.')[0].split('_')[1].strip('0')))
			try:
				( items[header['_rlnDefocusU']], items[header['_rlnDefocusV']], items[header['_rlnDefocusAngle']] ) = \
						defocus[ ( num, int(eval(items[header['_rlnCoordinateX']])), int(eval(items[header['_rlnCoordinateY']])) ) ]
				outfile.write(' \t'.join(items) + '\n')
			except KeyError:
				print 'Particle coordinates not found. Something went wrong...'
				exit()
		elif not readHeader:
			outfile.write(line)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('files', metavar='fileName', type=str, nargs='+', help='input and output file names')
	parser.add_argument('--original', action='store_true', help='use imageOriginalName instead of imageName')
	args = parser.parse_args()
	defocus = getDefocus(args.files[2])
	if args.original:
		replaceDefocus(defocus, args.files[1], args.files[0], 1)
	else:
		replaceDefocus(defocus, args.files[1], args.files[0], 0)

if __name__ == '__main__':
	main()
