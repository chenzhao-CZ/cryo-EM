##################################################################################
# Chen Zhao
# czhao@rockefeller.edu
# degenerate a star file from relion 3.1 into relion 3.0- format
# assign beam tilt class based on optics group
# can only handle star files with data collected at the same pixel size
# to run:
# python relion3.1to3.py infile.star outfile.star
##################################################################################

import sys
from collections import OrderedDict

class optical:
	def __init__(self, para1, para2, para3, para4, para5, para6, para7, para8):
		self.OpticsGroup = para1
		self.AmplitudeContrast = para2
		self.SphericalAberration = para3
		self.Voltage = para4
		self.ImagePixelSize = para5
		self.ImageSize = para6
		self.BeamTiltX = para7
		self.BeamTiltY = para8

def convert(infileName, outfileName):
	headerOptics = OrderedDict()
	headerParticles = OrderedDict()
	with open(infileName, 'r') as infile, open(outfileName, 'w') as outfile:
		opticalGroups = []
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
			elif optics and not particles:
				if not finishOptics:
					if line.startswith('_rln'):
						headerCountOptics += 1
						entry = line.split(' ')
						headerOptics[entry[0]] = eval(entry[1][1:]) - 1
					elif headerCountOptics:
						if line.strip():
							items = line[:-1].split()
							if '_rlnBeamTiltX' in headerOptics.keys() and '_rlnBeamTiltY' in headerOptics.keys():
								opticalGroups.append( optical(
									items[headerOptics['_rlnOpticsGroup']] , \
									items[headerOptics['_rlnAmplitudeContrast']] , \
									items[headerOptics['_rlnSphericalAberration']] , \
									items[headerOptics['_rlnVoltage']] , \
									items[headerOptics['_rlnImagePixelSize']] , \
									items[headerOptics['_rlnImageSize']] , \
									items[headerOptics['_rlnBeamTiltX']] , \
									items[headerOptics['_rlnBeamTiltY']] \
									) )
								tilt = 1
							else:
								opticalGroups.append( optical(
									items[headerOptics['_rlnOpticsGroup']] , \
									items[headerOptics['_rlnAmplitudeContrast']] , \
									items[headerOptics['_rlnSphericalAberration']] , \
									items[headerOptics['_rlnVoltage']] , \
									items[headerOptics['_rlnImagePixelSize']] , \
									items[headerOptics['_rlnImageSize']] , \
									None, None, \
									) )
						else:
							pixel = opticalGroups[0].ImagePixelSize
							size = opticalGroups[0].ImageSize
							for item in opticalGroups[1:]:
								if item.ImagePixelSize != pixel or item.ImageSize != size:
									print 'Error! Datasets with different shapes are not allowed'
									exit()
							finishOptics = 1
				else:
					if line.startswith('data_particles'):
						outfile.write('\ndata_\n')
						particles = 1
			elif optics and particles:
				if line.startswith('_rln'):
					headerCountParticles += 1
					entry = line.split(' ')
					headerParticles[entry[0]] = eval(entry[1][1:]) - 1
				elif line.strip() and headerCountParticles:
					if not finishHeaderParticles:
						delete = -1
						for key, num in headerParticles.items():
							if delete < 0:
								if key == '_rlnOpticsGroup':
									delete = num
									headerCountParticles -= 1
							else:
								headerParticles[key] = num - 1
						cols = ['_rlnAmplitudeContrast', '_rlnSphericalAberration', '_rlnVoltage', '_rlnImagePixelSize', \
								'_rlnMagnification', '_rlnBeamTiltClass', '_rlnBeamTiltX', '_rlnBeamTiltY']
						if tilt:
							for col in cols:
							 	if col not in headerParticles:
									headerCountParticles += 1
									headerParticles[col] = headerCountParticles - 1
						else:
							for col in cols[:-3]:
								 	if col not in headerParticles:
										headerCountParticles += 1
										headerParticles[col] = headerCountParticles - 1
						for key, num in headerParticles.items():
							if key != '_rlnOpticsGroup':
								if key == '_rlnOriginXAngst':
									outfile.write('_rlnOriginX' + ' #' + str(num + 1) + '\n')
								elif key == '_rlnOriginYAngst':
									outfile.write('_rlnOriginY' + ' #' + str(num + 1) + '\n')
								elif key == '_rlnImagePixelSize':
									outfile.write('_rlnDetectorPixelSize' + ' #' + str(num + 1) + '\n')
								else:
									outfile.write(key + ' #' + str(num + 1) + '\n')
						finishHeaderParticles = 1
						writeParticle(line, headerParticles, opticalGroups, tilt, outfile)
					else:
						writeParticle(line, headerParticles, opticalGroups, tilt, outfile)
				elif not headerCountParticles:
					outfile.write(line)

def writeParticle(line, headerParticles, opticalGroups, tilt, outfile):
	items = line[:-1].split()
	index = items[headerParticles['_rlnOpticsGroup']]
	opticParameters = opticalGroups[eval(index) - 1]
	items.pop(headerParticles['_rlnOpticsGroup'])
	items = items + [ opticParameters.AmplitudeContrast, opticParameters.SphericalAberration, \
			opticParameters.Voltage, opticParameters.ImagePixelSize ]
	try:
		items[headerParticles['_rlnOriginXAngst']] = str(  \
				eval(items[headerParticles['_rlnOriginXAngst']]) / \
				eval(items[headerParticles['_rlnImagePixelSize']]) )
		items[headerParticles['_rlnOriginYAngst']] = str(  \
				eval(items[headerParticles['_rlnOriginYAngst']]) / \
				eval(items[headerParticles['_rlnImagePixelSize']]) )
	except KeyError:
		pass
	items = items + ['10000.000000']
	if tilt:
		items = items + [ index , opticParameters.BeamTiltX, opticParameters.BeamTiltY ] 
	outfile.write(' \t'.join(items) + '\n')

def main():
	convert(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
	main()
