########################################################################################################################
# Author: Chen Zhao (czhao@rockefeller.edu)
# count the number of appearances of same particle in .star file from a 3D classification job after symmetry expansion
# write out .star file containing particles appearing 1, 2, 3, and 4 times
#	w/o redundant particles removed
# work with star files from both Relion 3.1 and 3-
# To run:
# python countSameParticleRelion.py particle.star
########################################################################################################################

import sys
from collections import OrderedDict

def countStar(infileName):
	headerContent = ''
	print 'counting...'
	with open(infileName, 'r') as infile:
		for line in infile:
			headerContent += line
			if line.startswith('data_optics'):
				( particles, particlesInfo, headerContent ) = countRelion31(infile, headerContent)
			elif line.startswith('data_'):
				( particles, particlesInfo, headerContent ) = countRelion3(infile, headerContent)
	return particles, particlesInfo, headerContent

def countRelion31(infile, headerContent):
	particles = OrderedDict()
	particlesInfo = OrderedDict()
	headerParticles = {}
	startParticles = 0
	count = 0
	readHeader = 0
	for line in infile:
		if not startParticles:
			headerContent += line
			if line.startswith('data_particles'):
				startParticles = 1
		else:
			if line.startswith('_rln'):
				readHeader = 1
				entry = line.split(' ')
				headerParticles[entry[0]] = eval(entry[1][1:]) - 1
				headerContent += line
			elif line.strip() and readHeader:
				items = line[:-1].split()
				count += 1
				print 'processing particle: ' + str(count)
				path = items[headerParticles['_rlnImageName']].split('@')
				key = ( path[1], path[0] )
				if key not in particles.keys():
					particles[key] = 1
					particlesInfo[key] = [line]
				else:
					particles[key] += 1
					particlesInfo[key].append(line)
			else:
				headerContent += line
	return particles, particlesInfo, headerContent

def countRelion3(infile, headerContent):
	particles = OrderedDict()
	particlesInfo = OrderedDict()
	header = {}
	count = 0
	readHeader = 0
	for line in infile:
		if line.startswith('_rln'):
			readHeader = 1
			entry = line.split(' ')
			header[entry[0]] = eval(entry[1][1:]) - 1
			headerContent += line
		elif line.strip() and readHeader:
			items = line[:-1].split()
			count += 1
			print 'processing particle: ' + str(count)
			path = items[header['_rlnImageName']].split('@')
			key = ( path[1], path[0] )
			if key not in particles.keys():
				particles[key] = 1
				particlesInfo[key] = [line]
			else:
				particles[key] += 1
				particlesInfo[key].append(line)
		else:
			headerContent += line
	return particles, particlesInfo, headerContent

def reverseSort(particles):
	# sort particles by number of appearances
	particleCount = {
			 1: [],
			 2: [],
			 3: [],
			 4: []
			 }
	for path, count in particles.items():
		particleCount[count].append(path)
	return particleCount

def writeStar(data, sortedPath, header, filename):
	# initiate files
	one = open(filename[:-5] + '-1.star', 'w')
	oneuni = open(filename[:-5] + '-1-unique.star', 'w')
	two = open(filename[:-5] + '-2.star', 'w')
	twouni = open(filename[:-5] + '-2-unique.star', 'w')
	three = open(filename[:-5] + '-3.star', 'w')
	threeuni = open(filename[:-5] + '-3-unique.star', 'w')
	four = open(filename[:-5] + '-4.star', 'w')
	fouruni = open(filename[:-5] + '-4-unique.star', 'w')
	# write header
	files = [one, oneuni, two, twouni, three, threeuni, four, fouruni]
	for item in files:
		item.write(header)
	# write particles appearing four times
	for particlePath in sortedPath[4]:
		fouruni.write(data[particlePath][0])
		for line in data[particlePath]:
			four.write(line)
	print 'Number of particles appearing 4 times: ' + str(len(sortedPath[4]))
	# write particles appearing three times
	for particlePath in sortedPath[3]:
		threeuni.write(data[particlePath][0])
		for line in data[particlePath]:
			three.write(line)
	print 'Number of particles appearing 3 times: ' + str(len(sortedPath[3]))
	# write particles appearing twice
	for particlePath in sortedPath[2]:
		twouni.write(data[particlePath][0])
		for line in data[particlePath]:
			two.write(line)
	print 'Number of particles appearing twice: ' + str(len(sortedPath[2]))
	# write particles appearing once
	for particlePath in sortedPath[1]:
		oneuni.write(data[particlePath][0])
		for line in data[particlePath]:
			one.write(line)
	print 'Number of particles appearing once: ' + str(len(sortedPath[1]))
	# closing files
	for item in files:
		item.close()

def main():
	counts, data, header = countStar(sys.argv[1])
	sortedPath = reverseSort(counts)
	writeStar(data, sortedPath, header, sys.argv[1])

if __name__ == '__main__':
	main()
