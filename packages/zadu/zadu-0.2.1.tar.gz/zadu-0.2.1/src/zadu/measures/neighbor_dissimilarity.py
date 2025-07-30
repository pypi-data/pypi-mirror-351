from sklearn.neighbors import kneighbors_graph
import numpy as np
from .utils import knn



def measure(orig, emb, k=20, snn_info=None, knn_info=None):
	"""
	Compute neighbor dissimilarity (ND) of the embedding
	INPUT:
		ndarray: orig: original data
		ndarray: emb: embedded data
		int: k: number of nearest neighbors to consider
		tuple: knn_info: precomputed k-nearest neighbors and rankings of the original and embedded data (Optional)
	OUTPUT:
		dict: neighbor dissimilarity (ND)
	"""
	
	if snn_info is None:
		if knn_info is None:
			orig_SNN_graph = knn.snn(orig, k, directed=False)
			emb_SNN_graph = knn.snn(emb, k, directed=False)
		else:
			orig_SNN_graph = knn.snn(orig, k, knn_indices=knn_info[0], directed=False)
			emb_SNN_graph = knn.snn(emb, k, knn_indices=knn_info[1], directed=False)
	
	else:
		orig_SNN_graph, emb_SNN_graph = snn_info

	D = (orig_SNN_graph - emb_SNN_graph) / k

	D_plus = D[D > 0]
	D_minus = D[D < 0]

	dissim_plus = np.sqrt(np.sum(D_plus**2))
	dissim_minus = np.sqrt(np.sum(D_minus**2))

	nd = max(dissim_plus, dissim_minus)

	return {
			"neighbor_dissimilarity": nd
	}