#Mateja Stojanovic
#Schüler der HTL Anichstraße
#geschrieben am 26.09.2024
import numpy
from xyz_lib import *
from rot_lib import *

# Liest die Atome (a) und deren Koordinaten (c) aus der Datei 'aspirin.xyz'
a, c = read_xyz('aspirin.xyz')

# Konvertiert die Koordinatenliste 'c' in ein NumPy-Array für mathematische Operationen
koordinaten = numpy.array(c)

# Transponiert die Koordinatenmatrix, sodass die Achsen vertauscht werden (z.B. von (N, 3) auf (3, N)),
# was nützlich für Matrixmultiplikationen ist
koordinaten2 = numpy.transpose(koordinaten)

# Erstellt eine Rotationsmatrix basierend auf den Winkeln (100, 187, 69) in Grad.
neue_matrix = rotate(100, 187, 69)

# Multipliziert die Rotationsmatrix 'neue_matrix' mit der transponierten Koordinatenmatrix.
# Dies rotiert die Koordinaten im 3D-Raum entsprechend den angegebenen Winkeln.
matrix2 = numpy.matmul(neue_matrix, koordinaten2)

# Transponiert die resultierende Matrix zurück, um die ursprüngliche Form der Koordinaten wiederherzustellen (N, 3).
matrix_ges = numpy.transpose(matrix2)

# Schreibt die neue XYZ-Datei 'aspirin3.xyz' mit den Atomen 'a' und den rotierten Koordinaten 'matrix_ges'.
write_xyz('aspirin3.xyz', a, matrix_ges)
