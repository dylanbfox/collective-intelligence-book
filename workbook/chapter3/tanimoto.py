def tanimoto(v1, v2):
	c1, c2, shr = 0,0,0

	for i in range(len(v1)):
		if v1[i] != 0: # in v1
			c1 += 1

		if v2[i] != 0: # in v2
			c2 += 1

		if v1[i] != 0 and v2[i] != 0: # in both
			shr += 1

	return 1.0 - (float(shr) / (c1 + c2 - shr))