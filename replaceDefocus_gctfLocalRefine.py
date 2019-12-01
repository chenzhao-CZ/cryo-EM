#########################################################################################################
# Chen Zhao
# czhao@rockefeller.edu
# replace defocus from values after Gctf local refine
# to run:
# replaceDefocus_gctfLocalRefine.py particles-to-be-replaced.star new-file.star path-to-_local.star
#########################################################################################################

import sys
import os

def getDefocus(path):
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

def replaceDefocus(defocus, outfilename, particles):
	print 'replacing defocus values in input particle.star...'
	header = {}
	with open(particles, 'r') as infile, open(outfilename, 'w') as outfile:
		readHeader = 0
		for line in infile:
			# parse header
			if line.startswith('_rln'):
				readHeader = 1
				entry = line.split(' ')
				header[entry[0]] = eval(entry[1][1:]) - 1
				outfile.write(line)
			# parse entries
			elif line.strip() and readHeader:
				items = line[:-1].split()
				#num = int(eval(items[header['_rlnImageName']].split('/')[-1].split('.')[0].split('_')[1].strip('0')))
				num = int(eval(items[header['_rlnImageOriginalName']].split('/')[-1].split('.')[0].split('_')[1].strip('0')))
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
	defocus = getDefocus(sys.argv[3])
	replaceDefocus(defocus, sys.argv[2], sys.argv[1])

if __name__ == '__main__':
	main()
