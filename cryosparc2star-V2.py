##############################################################################################################################
# Chen Zhao
# czhao@rockefeller.edu
# convert .cs to .star (only work for cryosparc V2)
# I wrote this to keep random subset after refinement
# to run:
# python cryosparc2star.py --refined cs-to-be-converted.cs --star star-imported-into-cryosparc.star --out out-file-name.star 
#############################################################################################################################

import numpy as np
import argparse
import sys
from collections import OrderedDict

class pyemFunctions:
	# pyem by Daniel Asarnow
	# https://github.com/asarnow/pyem.git
	def __init__(self):
		print 'Load functions from pyem by Daniel Asarnow'

	def expmap(self, e):
		"""Convert axis-angle vector into 3D rotation matrix"""
		theta = np.linalg.norm(e)
		if theta < 1e-16:
			return np.identity(3, dtype=e.dtype)
		w = e / theta
		k = np.array([[0, w[2], -w[1]],
		              [-w[2], 0, w[0]],
		              [w[1], -w[0], 0]], dtype=e.dtype)
		r = np.identity(3, dtype=e.dtype) + np.sin(theta) * k + (1 - np.cos(theta)) * np.dot(k, k)
		return r
	
	def rot2euler(self, r):
		"""Decompose rotation matrix into Euler angles"""
		# assert(isrotation(r))
		# Shoemake rotation matrix decomposition algorithm with same conventions as Relion.
		epsilon = np.finfo(np.double).eps
		abs_sb = np.sqrt(r[0, 2] ** 2 + r[1, 2] ** 2)
		if abs_sb > 16 * epsilon:
		    gamma = np.arctan2(r[1, 2], -r[0, 2])
		    alpha = np.arctan2(r[2, 1], r[2, 0])
		    if np.abs(np.sin(gamma)) < epsilon:
		    	sign_sb = np.sign(-r[0, 2]) / np.cos(gamma)
		    else:
		    	sign_sb = np.sign(r[1, 2]) if np.sin(gamma) > 0 else -np.sign(r[1, 2])
		    beta = np.arctan2(sign_sb * abs_sb, r[2, 2])
		else:
		    if np.sign(r[2, 2]) > 0:
		        alpha = 0
		        beta = 0
		        gamma = np.arctan2(-r[1, 0], r[0, 0])
		    else:
		        alpha = 0
		        beta = np.pi
		        gamma = np.arctan2(r[1, 0], -r[0, 0])
		return [alpha, beta, gamma]

pyem = pyemFunctions()

def getInfo(instar):
	coordinate = {}
	header = {}
	with open(instar, 'r') as star:
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
				path = items[header['_rlnImageName']].split('@')
				idx = ( path[0].lstrip('0'), path[1].split('/')[-1] )
				infor = ( items[header['_rlnImageName']], items[header['_rlnImageOriginalName']], \
						items[header['_rlnCoordinateX']], items[header['_rlnCoordinateY']], items[header['_rlnMicrographName']], \
								items[header['_rlnMagnification']] )
				if idx not in coordinate.keys():
					coordinate[idx] = infor
				else:
					if infor != coordinate[idx]:
						print 'Error! Input star file is not consistent'
	return coordinate


def writeSTAR(refine, coordinates, outfile):
	header = [ \
			'_rlnAmplitudeContrast', \
			'_rlnDetectorPixelSize', \
			'_rlnDefocusU', \
			'_rlnDefocusV', \
			'_rlnDefocusAngle', \
			'_rlnAnglePsi', \
			'_rlnAngleRot', \
			'_rlnAngleTilt',\
			'_rlnOriginX', \
			'_rlnOriginY', \
			'_rlnImageName', \
			'_rlnImageOriginalName', \
			'_rlnCoordinateX', \
			'_rlnCoordinateY', \
			'_rlnMicrographName', \
			'_rlnMagnification', \
			'_rlnPhaseShift', \
			'_rlnSphericalAberration', \
			'_rlnVoltage', \
			'_rlnRandomSubset' \
			]
	with open(outfile, 'w') as out:
		out.write('\ndata_\n\nloop_\n')
		for counter, item in enumerate(header):
			out.write(header[counter] + ' #' + str(counter + 1) + '\n')
		cs = np.load(refine)
		for particle in cs:
			angles = np.rad2deg(pyem.rot2euler(pyem.expmap(particle['alignments3D/pose'])))
			idx = ( str(particle['blob/idx'] + 1),  particle['blob/path'].split('/')[-1] )
			try:
				infor = coordinates[idx]
				out.write( \
						str(particle['ctf/amp_contrast']) + ' \t' + \
						str(particle['blob/psize_A']) + ' \t' + \
						str(particle['ctf/df1_A']) + ' \t' + \
						str(particle['ctf/df2_A']) + ' \t' + \
						str(np.rad2deg(particle['ctf/df_angle_rad'])) + ' \t' + \
						str(angles[2]) + ' \t' + \
						str(angles[0]) + ' \t' + \
						str(angles[1]) + ' \t' + \
						str(particle['alignments3D/shift'][0]) + ' \t' + \
						str(particle['alignments3D/shift'][1]) + ' \t' + \
						infor[0] + ' \t' + \
						infor[1] + ' \t' + \
						infor[2] + ' \t' + \
						infor[3] + ' \t' + \
						infor[4] + ' \t' + \
						infor[5] + ' \t' + \
						str(np.rad2deg(particle['ctf/phase_shift_rad'])) + ' \t' + \
						str(particle['ctf/cs_mm']) + ' \t' + \
						str(particle['ctf/accel_kv']) + ' \t' + \
						str(particle['alignments3D/split'] + 1) + '\n' \
						)
			except KeyError:
				print 'Error! Particle not found'
				exit()
		out.close()

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--cs', help='cs file from cryosparc refinement job')
	parser.add_argument('--star', help='original star file imported into cryosparc')
	parser.add_argument('--out', help='output file name')
	args = parser.parse_args()
	coordinates = getInfo(args.star)
	writeSTAR(args.cs, coordinates, args.out)

if __name__ == "__main__":
	main()
