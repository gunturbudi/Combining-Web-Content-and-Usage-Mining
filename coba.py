

def flatten(matrix):
    flat_matrix = []
    for a in matrix:
    	flat_matrix.extend(a)
    return flat_matrix

def getPresedenceMatrix(seq,unique,flatting):
	seq.insert(0,0)
	seq.append(0)
	
	matrix = []

	for a in range(0,len(unique)):
		temp = []
		for b in range(0,len(unique)):
			temp.append(0)
		matrix.append(temp)

	for i in range(0,len(seq)):
		for j in range(i+1,len(seq)):
			matrix[seq[i]][seq[j]] = matrix[seq[i]][seq[j]] + 1

	for a in range(0,len(unique)):
		jml = float(sum(matrix[a]))
		for b in range(0,len(unique)):
			if jml!=0:
				matrix[a][b] = float(matrix[a][b]) / jml
			else:
				matrix[a][b] = 0

	if(flatting):
		matrix = flatten(matrix)

	return matrix

seq = [1,3,1]
unique = [0,1,2,3]

print getPresedenceMatrix(seq,unique,1)


