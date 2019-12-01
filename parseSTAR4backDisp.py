##################################################################################
# Chen Zhao
# czhao@rockefeller.edu
# backdisplay to coordinate star file from particle.star
# currently work only for relion 3.0-, upgrading soon
# this script will generate a new directory call Backdisplay with all coordiantes
# to run:
# python parseSTAR4backdisplay.py particles.star
#################################################################################

import sys
import subprocess as sp
import os

class particle:
	def __init__(self, x, y, path):
		self.x = x
		self.y = y
		self.path = path

class anaParticles:
	def __init__(self, filename):
		self.particles = {}
		self.infile = filename
		self.header = {}

	def parse(self):
		with open(self.infile, 'r') as star:
			readHeader = 0
			for line in star:
				# parse header
				if line.startswith('_rln'):
					readHeader = 1
					entry = line.split(' ')
					self.header[entry[0]] = eval(entry[1][1:]) - 1
				# parse entries
				elif line.strip() and readHeader:
					items = line[:-1].split()
					path = items[self.header['_rlnMicrographName']]
					if path not in self.particles.keys():
						self.particles[path] = [ particle(items[self.header['_rlnCoordinateX']], items[self.header['_rlnCoordinateY']], path) ]
					else:
						self.particles[path].append( particle(items[self.header['_rlnCoordinateX']], items[self.header['_rlnCoordinateY']], path) )

	def writeParticles(self):
		if not os.path.isdir('BackDisplay'):
			sp.call(['mkdir', 'BackDisplay'])
		os.chdir('BackDisplay')
		for key, value in self.particles.items():
			outfile = key.split('/')[-1][:-4] + '_backdisplay.star'
			with open(outfile, 'w') as out:
				out.write('\ndata_\n\nloop_\n_rlnCoordinateX #1\n_rlnCoordinateY #2\n')
				for entry in value:
					out.write(entry.x + '     ' + entry.y + '\n')
	
	def printHeader(self):
		for key, val in self.header.items():
			print key, '->', val

def main():
	particles = anaParticles(sys.argv[1])
	particles.parse()
	particles.writeParticles()

if __name__ == "__main__":
	main()
