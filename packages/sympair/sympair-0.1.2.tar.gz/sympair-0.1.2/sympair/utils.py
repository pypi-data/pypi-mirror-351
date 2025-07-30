import numpy as np

def symbol_number(symbols):
    """
    ["Sr", "Ti", "O",  "O" , "O"] -> ["Sr1", "Ti1", "O1", "O2", "O3"]
    """
    symbol_dict = {}
    new_symbols = []
    for s in symbols:
        if s not in symbol_dict:
            symbol_dict[s] = 1
        else:
            symbol_dict[s] += 1
        new_symbols.append(s + str(symbol_dict[s]))
    return new_symbols


def test_symbol_number():
    symbols = ["Sr", "Ti", "O",  "O" , "O"]
    assert symbol_number(symbols) == ["Sr1", "Ti1", "O1", "O2", "O3"]
    assert symbol_number(["Sr", "Sr", "Sr"]) == ["Sr1", "Sr2", "Sr3"]
    assert symbol_number(["Sr",  "O", "Sr"]) ==  ["Sr1", "O1", "Sr2"]
    print("test_symbol_number passed")


def inverse_ijR(i, j, R):
    """
    Return the inverse of (i, j, R)
    """
    return j, i, tuple(-Rq for Rq in R)

    
def standardize_ijR(i, j, R):
    """
    Return a standard form of (i, j, R), reversed. 
    """
    for v, Rv in enumerate(R):
        if Rv < 0:
            return  (j, i, tuple(-Rq for Rq in R)), True
        elif Rv > 0:
            return (i, j, R), False
    if R == (0, 0, 0) and i > j:
        return (j, i, R), True
    return (i, j, R), False

def is_identity_matrix(matrix, atol=1e-6):
    """
    Return True if the matrix is an identity matrix.
    consider the floating point error. Use numpy.
    """
    matrix = np.array(matrix)
    return np.allclose(matrix, np.eye(matrix.shape[0]), atol=atol)

def test_is_identity_matrix():
    """
    Test is_identity_matrix
    """
    assert is_identity_matrix([[1, 0], [0, 1]])
    assert is_identity_matrix([[1, 0], [0, 1]], atol=1e-7)
    assert not is_identity_matrix([[1, 0], [1e-6, 1]], atol=1e-8)
    assert not is_identity_matrix([[1, 0], [0, 1.0001]])
    assert is_identity_matrix([[1, 0], [0, 1.0001]], atol=1e-3)
    print("test_is_identity_matrix passed")

        
def test_standardize_ijR():
    assert standardize_ijR(0, 1, (0, 0, 0)) == ((0, 1, (0, 0, 0)), False)
    assert standardize_ijR(1, 0, (0, 0, 0)) == ((0, 1, (0, 0, 0)), True)
    assert standardize_ijR(0, 1, (1, 0, 0)) == ((0, 1, (1, 0, 0)), False)
    assert standardize_ijR(1, 0, (1, 0, 0)) == ((1, 0, (1, 0, 0)), False)
    assert standardize_ijR(0, 1, (-1, 0, 0)) ==( (1, 0, (1, 0, 0)), True)
    assert standardize_ijR(1, 0, (-1, 0, 0)) ==( (0, 1, (1, 0, 0)), True)
    assert standardize_ijR(0, 1, (0, 1, 0)) == ((0, 1, (0, 1, 0)), False)
    assert standardize_ijR(1, 0, (0, 1, 0)) == ((1, 0, (0, 1, 0)), False)
    assert standardize_ijR(0, 1, (0, -1, 0)) ==( (1, 0, (0, 1, 0)), True)
    assert standardize_ijR(1, 0, (0, -1, 0)) ==( (0, 1, (0, 1, 0)), True)
    assert standardize_ijR(0, 1, (0, 0, 1)) == ((0, 1, (0, 0, 1)), False)
    assert standardize_ijR(1, 0, (0, 0, 1)) == ((1, 0, (0, 0, 1)), False)
    assert standardize_ijR(0, 1, (0, 0, -1)) ==( (1, 0, (0, 0, 1)), True)
    assert standardize_ijR(1, 0, (0, 1, -1)) ==( (1, 0, (0, 1, -1)), False)
    assert standardize_ijR(1, 0, (0, -1, 1)) ==( (0, 1, (0, 1, -1)), True)


 

if __name__ == "__main__":
    test_symbol_number()
    test_standardize_ijR()
    test_is_identity_matrix()

