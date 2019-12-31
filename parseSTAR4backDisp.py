############################################################################################
# Chen Zhao
# czhao@rockefeller.edu
# backdisplay to coordinate star file from particle.star
# this script will generate a new directory call Backdisplay with all coordiantes
# can handle star files from both relion 3.1 and relion 3-
# to run:
# python parseSTAR4backdisplay.py particles.star
# python parseSTAR4backdisplay.py particles.star --recenter to recenter before backdisplay
############################################################################################

import subprocess as sp
import os
import argparse

class particle:
	def __init__(self, x, y, path):
		self.x = x
		self.y = y
		self.path = path

class anaParticles:
	def __init__(self, filename, recenter):
		self.particles = {}
		self.infile = filename
		self.header = {}
		self.recenter = recenter 

	def parse(self):
		with open(self.infile, 'r') as star:
			self.readHeader = 0
			for line in star:
				if line.startswith('data_optics'):
					self.__relion31(star)
				elif line.startswith('data_'):
					self.__relion3(star)

	def __relion31(self, star):
		particles = 0
		pix = {}
		headerOptics = {}
		for line in star:
			if not particles:
				if line.startswith('_rln'):
					entry = line.split(' ')
					headerOptics[entry[0]] = eval(entry[1][1:]) - 1
				elif line.startswith('data_particles'):
					particles = 1
				elif headerOptics and line.strip() and '#' not in line:
					items = line[:-1].split()
					pix[items[headerOptics['_rlnOpticsGroup']]] = items[headerOptics['_rlnImagePixelSize']]
			else:
				if line.startswith('_rln'):
					self.readHeader = 1
					entry = line.split(' ')
					self.header[entry[0]] = eval(entry[1][1:]) - 1
				elif line.strip() and self.readHeader:
					items = line[:-1].split()
					path = items[self.header['_rlnMicrographName']]
					if self.recenter:
						X = str( eval(items[self.header['_rlnCoordinateX']]) - eval(items[self.header['_rlnOriginXAngst']]) / eval(pix[items[self.header['_rlnOpticsGroup']]]) )
						Y = str( eval(items[self.header['_rlnCoordinateY']]) - eval(items[self.header['_rlnOriginYAngst']]) / eval(pix[items[self.header['_rlnOpticsGroup']]]) )
					else:
						X = items[self.header['_rlnCoordinateX']]
						Y = items[self.header['_rlnCoordinateY']]
					if path not in self.particles.keys():
						self.particles[path] = [ particle(X, Y, path) ]
					else:
						self.particles[path].append( particle(X, Y, path) )

	def __relion3(self, star):
		for line in star:
			if line.startswith('_rln'):
				self.readHeader = 1
				entry = line.split(' ')
				self.header[entry[0]] = eval(entry[1][1:]) - 1
			elif line.strip() and self.readHeader:
				items = line[:-1].split()
				path = items[self.header['_rlnMicrographName']]
				if self.recenter:
					X = str( eval(items[self.header['_rlnCoordinateX']]) - eval(items[self.header['_rlnOriginX']]) )
					Y = str( eval(items[self.header['_rlnCoordinateY']]) - eval(items[self.header['_rlnOriginY']]) )
				else:
					X = items[self.header['_rlnCoordinateX']]
					Y = items[self.header['_rlnCoordinateY']]
				if path not in self.particles.keys():
					self.particles[path] = [ particle(X, Y, path) ]
				else:
					self.particles[path].append( particle(X, Y, path) )

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
	parser = argparse.ArgumentParser()
	parser.add_argument('fileName', metavar='fileName', type=str, help='input file name')
	parser.add_argument('--recenter', action='store_true', help='shift particles by rlnOrigin')
	args = parser.parse_args()
	particles = anaParticles(args.fileName, args.recenter)
	particles.parse()
	particles.writeParticles()

if __name__ == "__main__":
	main()
