##################################################################################
# Chen Zhao
# czhao@rockefeller.edu
# relion 3.1: 
# assign optics group based on beam tilt class at RU Krios 1
# if _rlnBeamTiltClass was present in the old star file, delete it
# However, this needs to start from a relion3.1 star file
# to run:
# python opticsGroupByTilt.py infile.star outfile.star
##################################################################################

import sys
from collections import OrderedDict

def tilt31(infileName, outfileName):
	headerOptics = OrderedDict()
	headerParticles = OrderedDict()
	with open(infileName, 'r') as infile, open(outfileName, 'w') as outfile:
		opticalGroupCount = 0
		headerCountOptics = 0
		headerCountParticles = 0
		finishHeaderParticles = 0
		tilt = 0
		optics = 0
		particles = 0
		finishOptics = 0
		opticalLine = ''
		for line in infile:
			if not optics and not particles:
				if line.startswith('data_optics'):
					optics = 1
					outfile.write(line)
				else:
					outfile.write(line)
			elif optics and not particles:
				if not finishOptics:
					if not headerCountOptics:
						outfile.write(line)
						if line.startswith('_rln'):
							headerCountOptics += 1
							entry = line.split(' ')
							headerOptics[entry[0]] = eval(entry[1][1:]) - 1
					else:
						if line.startswith('_rln'):
							headerCountOptics += 1
							entry = line.split(' ')
							headerOptics[entry[0]] = eval(entry[1][1:]) - 1
							outfile.write(line)
						elif line.strip():
							opticalGroupCount += 1
							opticalLine = line
							outfile.write(line)
						elif not line.strip():
							sampleLine = opticalLine.split()
							for index in range(opticalGroupCount * 8):
								outfile.write( '    \t' +  str(index + 2) + ' \topticsGroup' + str(index + 2) + ' \t' + \
										' \t'.join(sampleLine[2:]) + '\n' )
							finishOptics = 1
				else:
					outfile.write(line)
					if line.startswith('data_particles'):
						particles = 1
			elif optics and particles:
				if line.startswith('_rln'):
					headerCountParticles += 1
					entry = line.split(' ')
					headerParticles[entry[0]] = eval(entry[1][1:]) - 1
				elif line.strip() and headerCountParticles:
					if not finishHeaderParticles:
						for key, value in headerParticles.items():
							if not tilt:
								if key == '_rlnBeamTiltClass':
									beamtilt = value
									tilt = 1
									headerParticles.pop('_rlnBeamTiltClass')
								else:
									outfile.write(key + ' #' + str(value + 1) + '\n')
							else:
								headerParticles[key] = value - 1
								outfile.write(key + ' #' + str(value) + '\n')
						finishHeaderParticles = 1
					else:
						items = line[:-1].split()
						if tilt:
							items = items[:beamtilt] + items[beamtilt + 1:]
							tiltclass = int(eval(items[headerParticles['_rlnMicrographName']].split('/')[-1].split('.')[0].split('_')[1].strip('0'))) % 9 + 1
							items[headerParticles['_rlnOpticsGroup']] = str(tiltclass)
							outfile.write(' \t'.join(items) + '\n')
						else:
							tiltclass = int(eval(items[headerParticles['_rlnMicrographName']].split('/')[-1].split('.')[0].split('_')[1].strip('0'))) % 9 + 1
							items[headerParticles['_rlnOpticsGroup']] = str(tiltclass)
							outfile.write(' \t'.join(items) + '\n')
				elif not headerCountParticles:
					outfile.write(line)

def main():
	tilt31(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
	main()
