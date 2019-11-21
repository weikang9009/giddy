"""
Sequence analysis methods.
"""

__author__ = "Wei Kang <weikang9009@gmail.com>, Sergio J. Rey <sjsrey@gmail.com>"

__all__ = ["Sequence", "Sequence_OMtransition"]

import itertools
import numpy as np
import scipy.spatial.distance as d
from .markov import Markov


# def om_pair_dist(seq1, seq2, subs_mat, indel):
#     '''
#     Method for calculating the optimal matching distance between a pair of
#     sequences given a substitution cost matrix and the indel cost.
#
#     Arguments
#     ---------
#     seq1            : array
#                       (t1, ), the first sequence
#     seq2            : array
#                       (t2, ), the second sequence
#     subs_mat        : array
#                       (k, k), the matrix of substitution costs
#     indel           : float or array
#                       float: state-independent cost, array: state-dependent cost
#
#     Returns
#     -------
#     D               : array
#                       (t2+1, t1+1), score matrix: D[i+1,j+1] is the best
#                       score for aligning the substring, seq1[0:j] and seq2[0:i],
#                       and D[t2+1, t1+1] (or D[-1,-1]) is the global optimal score.
#
#     '''
#
#     t1 = len(seq1)
#     t2 = len(seq2)
#
#     D = np.zeros((t2 + 1, t1 + 1))
#     for j in range(1, t1 + 1):
#         D[0, j] = indel * j
#     for i in range(1, t2 + 1):
#         D[i, 0] = indel * i
#
#     for i in range(1, t2 + 1):
#         for j in range(1, t1 + 1):
#             gaps = D[i, j - 1] + indel
#             gapt = D[i - 1, j] + indel
#             match = D[i - 1, j - 1] + subs_mat[seq1[j - 1], seq2[i - 1]]
#             D[i, j] = min(match, gaps, gapt)
#     return D

def om_pair_dist(seq1, seq2, subs_mat, indel):
    '''
    Method for calculating the optimal matching distance between a pair of
    sequences given a substitution cost matrix and the indel cost.

    Arguments
    ---------
    seq1            : array
                      (t1, ), the first sequence. The input sequence should be
                      integars and start from 0.
    seq2            : array
                      (t2, ), the second sequence. The input sequence should be
                      integars and start from 0.
    subs_mat        : array
                      (k, k), the matrix of substitution costs
    indel           : float or array
                      float: state-independent cost, array: state-dependent cost

    Returns
    -------
    D               : array
                      (t2+1, t1+1), score matrix: D[i+1,j+1] is the best
                      score for aligning the substring, seq1[0:j] and seq2[0:i],
                      and D[t2+1, t1+1] (or D[-1,-1]) is the global optimal score.

    '''

    seq1 = np.asarray(seq1).astype(int)
    seq2 = np.asarray(seq2).astype(int)
    t1 = len(seq1)
    t2 = len(seq2)
    k = len(subs_mat)
    if np.isscalar(indel):
        indel = np.ones(k) * indel
    else:
        indel = np.asarray(indel)

    seq1_indel = indel[seq1]
    seq2_indel = indel[seq2]

    D = np.zeros((t2 + 1, t1 + 1))
    D[0, 1:] = np.cumsum(seq1_indel)
    D[1:, 0] = np.cumsum(seq2_indel)

    for i in range(1, t2 + 1):
        for j in range(1, t1 + 1):
            gaps = D[i, j - 1] + seq1_indel[j - 1]
            gapt = D[i - 1, j] + seq2_indel[i - 1]
            match = D[i - 1, j - 1] + subs_mat[seq1[j - 1], seq2[i - 1]]
            D[i, j] = min(match, gaps, gapt)
    return D

class Sequence_base(object):
    def __init__(self, y, subs_mat=None,
                 indel=None):

        y = np.asarray(y)
        merged = list(itertools.chain.from_iterable(y))
        self.classes = np.unique(merged)
        self.k = len(self.classes)
        self.n = len(y)
        # self.cluster_type = cluster_type
        self.label_dict = dict(zip(self.classes, range(self.k)))
        self.subs_mat = subs_mat
        self.indel = indel

        y_int = []
        for yi in y:
            y_int.append(list(map(self.label_dict.get, yi)))
        self.y_int = np.array(y_int)
        self.t = self.y_int.shape[1]


        # might want to move this to child class when refactoring
        if self.subs_mat is not None:
            self.subs_mat = np.asarray(self.subs_mat)
            # if len(subs_mat) != self.k:
            #     raise ValueError('Please specify a proper substitu')
            if len(indel) == 1:
                self.indel = np.ones(len(self.subs_mat)) * indel
            elif len(indel) == len(self.subs_mat):
                self.indel = np.asarray(self.indel)
            else:
                raise ValueError('Please specify a proper substitution matrix '
                                 'and a proper insertion/deletion cost ('
                                 'vector)!')

    # def _om_pair_dist(self, seq1, seq2):
    #     return om_pair_dist(seq1, seq2, self.subs_mat, self.indel)


    # def _om_pair_dist(self, seq1, seq2):
    #     '''
    #     Method for calculating the optimal matching distance between a pair of
    #     sequences given a substitution cost matrix and an indel cost.
    #
    #     Arguments
    #     ---------
    #     seq1            : array
    #                       (t1, ), the first sequence
    #     seq2            : array
    #                       (t2, ), the second sequence
    #
    #     Returns
    #     -------
    #     D               : array
    #                       (t2+1, t1+1), score matrix: D[i+1,j+1] is the best
    #                       score for aligning the substring, seq1[0:j] and seq2[0:i],
    #                       and D[t2+1, t1+1] (or D[-1,-1]) is the global optimal score.
    #
    #     '''
    #
    #     t1 = len(seq1)
    #     t2 = len(seq2)
    #
    #     D = np.zeros((t2 + 1, t1 + 1))
    #     for j in range(1, t1 + 1):
    #         D[0, j] = self.indel * j
    #     for i in range(1, t2 + 1):
    #         D[i, 0] = self.indel * i
    #
    #     for i in range(1, t2 + 1):
    #         for j in range(1, t1 + 1):
    #             gaps = D[i, j - 1] + self.indel
    #             gapt = D[i - 1, j] + self.indel
    #             match = D[i - 1, j - 1] + self.subs_mat[
    #                 seq1[j - 1], seq2[i - 1]]
    #             D[i, j] = min(match, gaps, gapt)
    #     return D

    def _om_dist(self, y_int):
        '''
        Method for calculating optimal matching distances between all
        sequence pairs.

        Arguments
        ---------
        y_int           : array
                          Encoded longitudinal data ready for optimal matching.

        Note
        ----
        This method is optimized to calculate the distance between unique
        sequences only in order to save computation time.

        '''

        y_str = []
        for i in y_int:
            y_str.append(''.join(list(map(str, i))))

        moves_str, unique_indices = np.unique(y_str, axis=0, return_index=True)
        moves_int = y_int[unique_indices]
        uni_num = len(moves_str)
        dict_move_index = dict(zip(map(tuple, moves_int), range(uni_num)))

        # dict_move_index = dict(zip(map(tuple, moves_str), range(uni_num)))

        # y_uni = moves_int
        uni_seq_dis_mat = np.zeros((uni_num, uni_num))
        for pair in itertools.combinations(range(uni_num), 2):
            seq1 = moves_int[pair[0]]
            seq2 = moves_int[pair[1]]
            uni_seq_dis_mat[pair[0], pair[1]] = om_pair_dist(seq1, seq2,
                                                             self.subs_mat,
                                                             self.indel)[-1,
                                                                         -1]
            # uni_seq_dis_mat[pair[0], pair[1]] = self._om_pair_dist(seq1,
            #                                                        seq2)[-1, -1]
        uni_seq_dis_mat = uni_seq_dis_mat + uni_seq_dis_mat.transpose()

        seq_dis_mat = np.zeros((self.n, self.n))
        for pair in itertools.combinations(range(self.n), 2):
            seq1 = y_int[pair[0]]
            seq2 = y_int[pair[1]]
            seq_dis_mat[pair[0], pair[1]] = uni_seq_dis_mat[
                dict_move_index[tuple(seq1)],
                dict_move_index[tuple(seq2)]]

        self.seq_dis_mat = seq_dis_mat + seq_dis_mat.transpose()

class Sequence_OMtransition(Sequence_base):

    def __init__(self, y, subs_state_mat=None, trans_mat=None, w=0,
                 trans_type=None,
                 subs_state_type=None, indel_state=None,
                 future=False):
        '''

        :param y:
        :param subs_state_mat:
        :param trans_mat:
        :param w:
        :param trans_type:
        :param subs_state_type:
        :param indel_state:
        :param future: whether to compare the last state.
        '''
        Sequence_base.__init__(self, y)
        self.w = w
        self.trans_mat = trans_mat
        self.trans_type = trans_type
        self.subs_state_type = subs_state_type
        if type(indel_state) is int:
            self.indel_state = np.ones(self.k) * indel_state
        else:
            self.indel_state = indel_state
        self.subs_state_mat = subs_state_mat

        # self.indel = 2
        y_uni = np.unique(self.y_int)
        dict_trans_state = {}
        trans_list = []
        for i, tran in enumerate(itertools.product(y_uni, y_uni)):
            trans_list.append(tran)
            dict_trans_state[tran] = i


        if trans_mat is None:
            if trans_type is None:
                raise ValueError("Please specify a proper `trans_mat` or "
                                 "`trans_type` to proceed!")
            else:
                if trans_type.lower() == "stable":
                    k_tran = np.ones((self.k, self.k))
                    np.fill_diagonal(k_tran, 0)
                elif trans_type.lower() == "markov":
                    p = Markov(self.y_int).p
                    # k_tran = (2 - (p + p.T)) / 2
                    k_tran = 1-p
                self.trans_mat = k_tran

        if subs_state_mat is None:
            if subs_state_type is None:
                raise ValueError("Please specify a proper `subs_state_type` or "
                                 "`subs_state_mat` and `indel_state` to "
                                 "proceed!")
            else:
                if subs_state_type.lower()=="constant":
                    k_subs = np.ones((self.k, self.k))
                    np.fill_diagonal(k_subs, 0)
                    self.subs_state_mat = k_subs
                    if self.indel_state is None:
                        self.indel_state = 5 * np.ones(self.k)


        k_trans = self.k ** 2
        self.subs_mat = np.zeros((k_trans, k_trans))
        self.indel = np.zeros(k_trans)
        for row in range(k_trans):
            row_tran = trans_list[row]
            self.indel[row] = w * self.indel_state[row_tran[0]] + (1-w) * \
                              self.trans_mat[row_tran[0], row_tran[1]]
            if self.indel[row] == 0:
                self.indel[row] = 1
            for col in range(k_trans):
                col_tran = trans_list[col]
                # substitution cost as a weighted average
                if future:
                    sub = self.subs_state_mat[row_tran[1], col_tran[1]]
                else:
                    sub = self.subs_state_mat[row_tran[0], col_tran[0]]
                self.subs_mat[row, col] = w * sub + \
                                          (1 - w) * (abs(self.trans_mat[row_tran[0],
                                                                row_tran[1]]
                                                         - self.trans_mat[col_tran[
                                                                      0],
                                                                  col_tran[
                                                                      1]]))


        # self.indel = 10 #temporary

        # Transform sequences of states into sequences of transitions.
        y_tran_index = np.zeros((self.n, self.t - 1), dtype=int)
        y_tran = []
        for i in range(self.t - 1):
            y_tran.append(list(zip(self.y_int[:, i], self.y_int[:, i + 1])))
        for i in range(self.y_int.shape[0]):
            for j in range(self.t - 1):
                y_tran_index[i, j] = dict_trans_state[y_tran[j][i]]
        # print(y_tran_index)
        self.y_tran_index = y_tran_index
        self._om_dist(y_tran_index)

class Sequence(object):
    """
    Pairwise sequence analysis.

    Dynamic programming if optimal matching.

    Parameters
    ----------
    y               : array
                      one row per sequence of neighborhood types for each
                      spatial unit. Sequences could be of varying lengths.
    subs_mat        : array
                      (k,k), substitution cost matrix. Should be hollow (
                      0 cost between the same type), symmetric and non-negative.
    dist_type       : string
                      "hamming": hamming distance (substitution only
                      and its cost is constant 1) from sklearn.metrics;
                      "markov": utilize empirical transition
                      probabilities to define substitution costs;
                      "interval": differences between states are used
                      to define substitution costs, and indel=k-1;
                      "arbitrary": arbitrary distance if there is not a
                      strong theory guidance: substitution=0.5, indel=1.
                      "tran": transition-oriented optimal matching. Sequence of
                      transitions. Based on :cite:`Biemann:2011`.
    indel           : float
                      insertion/deletion cost.
    cluster_type    : string
                      cluster algorithm (specification) used to generate
                      neighborhood types, such as "ward", "kmeans", etc.

    Attributes
    ----------
    seq_dis_mat     : array
                      (n,n), distance/dissimilarity matrix for each pair of
                      sequences
    classes         : array
                      (k, ), unique classes
    k               : int
                      number of unique classes
    label_dict      : dict
                      dictionary - {input label: int value between 0 and k-1 (k
                      is the number of unique classes for the pooled data)}

    Examples
    --------
    >>> import numpy as np

    1. Testing on unequal string sequences
    1.1 substitution cost matrix and indel cost are not given, and will be
    generated based on the distance type "interval"

    >>> seq1 = 'ACGGTAG'
    >>> seq2 = 'CCTAAG'
    >>> seq3 = 'CCTAAGC'
    >>> seqAna = Sequence([seq1,seq2,seq3],dist_type="interval")
    >>> seqAna.k
    4
    >>> seqAna.classes
    array(['A', 'C', 'G', 'T'], dtype='<U1')
    >>> seqAna.subs_mat
    array([[0., 1., 2., 3.],
           [1., 0., 1., 2.],
           [2., 1., 0., 1.],
           [3., 2., 1., 0.]])
    >>> seqAna.seq_dis_mat
    array([[ 0.,  7., 10.],
           [ 7.,  0.,  3.],
           [10.,  3.,  0.]])

    1.2 User-defined substitution cost matrix and indel cost

    >>> subs_mat = np.array([[0, 0.76, 0.29, 0.05],[0.30, 0, 0.40, 0.60],[0.16, 0.61, 0, 0.26],[0.38, 0.20, 0.12, 0]])
    >>> indel = subs_mat.max()
    >>> seqAna = Sequence([seq1,seq2,seq3], subs_mat=subs_mat, indel=indel)
    >>> seqAna.seq_dis_mat
    array([[0.  , 1.94, 2.46],
           [1.94, 0.  , 0.76],
           [2.46, 0.76, 0.  ]])

    1.3 Calculating "hamming" distance will fail on unequal sequences

    >>> seqAna = Sequence([seq1,seq2,seq3], dist_type="hamming")
    Traceback (most recent call last):
    ValueError: hamming distance cannot be calculated for sequences of unequal lengths!


    2. Testing on equal string sequences

    >>> seq1 = 'ACGGTAG'
    >>> seq2 = 'CCTAAGA'
    >>> seq3 = 'CCTAAGC'

    2.1  Calculating "hamming" distance

    >>> seqAna = Sequence([seq1,seq2,seq3], dist_type="hamming")
    >>> seqAna.seq_dis_mat
    array([[0., 6., 6.],
           [6., 0., 1.],
           [6., 1., 0.]])

    2.2 User-defined substitution cost matrix and indel cost (distance
    between different types is always 1 and indel cost is 2) - give the same
    sequence distance matrix as "hamming" distance

    >>> subs_mat = np.array([[0., 1., 1., 1.],[1., 0., 1., 1.],[1., 1., 0., 1.],[1., 1., 1., 0.]])
    >>> indel = 2
    >>> seqAna = Sequence([seq1,seq2,seq3], subs_mat=subs_mat, indel=indel)
    >>> seqAna.seq_dis_mat
    array([[0., 6., 6.],
           [6., 0., 1.],
           [6., 1., 0.]])

    2.3 User-defined substitution cost matrix and indel cost (distance
    between different types is always 1 and indel cost is 1) - give a
    slightly different sequence distance matrix from "hamming" distance since
    insertion and deletion is happening

    >>> subs_mat = np.array([[0., 1., 1., 1.],[1., 0., 1., 1.],[1., 1., 0.,1.],[1., 1., 1., 0.]])
    >>> indel = 1
    >>> seqAna = Sequence([seq1,seq2,seq3], subs_mat=subs_mat, indel=indel)
    >>> seqAna.seq_dis_mat
    array([[0., 5., 5.],
           [5., 0., 1.],
           [5., 1., 0.]])

    3. Not passing proper parameters will raise an error

    >>> seqAna = Sequence([seq1,seq2,seq3])
    Traceback (most recent call last):
    ValueError: Please specify a proper `dist_type` or `subs_mat` and `indel` to proceed!

    >>> seqAna = Sequence([seq1,seq2,seq3], subs_mat=subs_mat)
    Traceback (most recent call last):
    ValueError: Please specify a proper `dist_type` or `subs_mat` and `indel` to proceed!

    >>> seqAna = Sequence([seq1,seq2,seq3], indel=indel)
    Traceback (most recent call last):
    ValueError: Please specify a proper `dist_type` or `subs_mat` and `indel` to proceed!
    """

    def __init__(self, y, subs_mat=None, dist_type=None,
                 indel=None, cluster_type=None):

        y = np.asarray(y)
        merged = list(itertools.chain.from_iterable(y))
        self.classes = np.unique(merged)
        self.k = len(self.classes)
        self.n = len(y)
        self.indel = indel
        self.subs_mat = subs_mat
        self.cluster_type = cluster_type
        self.label_dict = dict(zip(self.classes, range(self.k)))

        y_int = []
        for yi in y:
            y_int.append(list(map(self.label_dict.get, yi)))
        y_int = np.array(y_int)

        if subs_mat is None or indel is None:
            if dist_type is None:
                raise ValueError("Please specify a proper `dist_type` or "
                                 "`subs_mat` and `indel` to proceed!")
            else:
                if dist_type.lower() == "interval":
                    self.indel = self.k - 1
                    self.subs_mat = np.zeros((self.k, self.k))
                    for i in range(0, self.k - 1):
                        for j in range(i + 1, self.k):
                            self.subs_mat[i, j] = j - i
                            self.subs_mat[j, i] = j - i
                    self._om_dist(y_int)

                elif dist_type.lower() == "hamming":
                    if len(y_int.shape) != 2:
                        raise ValueError(
                            'hamming distance cannot be calculated for '
                            'sequences of unequal lengths!')
                    hamming_dist = d.pdist(y_int, metric='hamming') * \
                                   y_int.shape[1]
                    self.seq_dis_mat = d.squareform(hamming_dist)

                elif dist_type.lower() == "arbitrary":
                    self.indel = 1
                    mat = np.ones((self.k, self.k)) * 0.5
                    np.fill_diagonal(mat, 0)
                    self.subs_mat = mat
                    self._om_dist(y_int)

                elif dist_type.lower() == "markov":
                    p = Markov(y_int).p
                    self.indel = 1
                    mat = (2 - (p + p.T)) / 2
                    np.fill_diagonal(mat, 0)
                    self.subs_mat = mat
                    self._om_dist(y_int)

                elif dist_type.lower() == "tran":  # sequence of transitions
                    self.indel = 2
                    y_uni = np.unique(y_int)
                    dict_trans_state = {}
                    trans_list = []
                    for i, tran in enumerate(itertools.product([-1], y_uni)):
                        trans_list.append(tran)
                        dict_trans_state[tran] = i
                    for i, tran in enumerate(itertools.product(y_uni, y_uni)):
                        trans_list.append(tran)
                        dict_trans_state[tran] = i + len(y_uni)
                    subs_mat = np.ones(
                        (self.k * (self.k + 1), self.k * (self.k +
                                                          1)))
                    np.fill_diagonal(subs_mat, 0)
                    for row in range(self.k ** 2):
                        row_index = row + self.k
                        row_tran = trans_list[row_index]
                        for col in range(self.k ** 2):
                            col_index = col + self.k
                            col_tran = trans_list[col_index]
                            subs_mat[row_index, col_index] = abs(int(row_tran[0] == row_tran[1]) -
                                                                 int(col_tran[0] == col_tran[1]))
                            # if row_tran[0] == row_tran[1]:
                            #     if col_tran[0] == col_tran[1]:
                            #         subs_mat[row_index, col_Index] = 0
                            # elif row_tran[0] != row_tran[1]:
                            #     if col_tran[0] != col_tran[1]:
                            #         subs_mat[row_index, col_Index] = 0
                    self.dict_trans_state = dict_trans_state
                    self.subs_mat = subs_mat

                    # Transform sequences of states into sequences of transitions.
                    y_int_ext = np.insert(y_int, 0, -1, axis=1)
                    y_tran_index = np.zeros_like(y_int)
                    y_tran = []
                    for i in range(y_int.shape[1]):
                        y_tran.append(
                            list(zip(y_int_ext[:, i], y_int_ext[:, i + 1])))
                    for i in range(y_int.shape[0]):
                        for j in range(y_int.shape[1]):
                            y_tran_index[i, j] = dict_trans_state[y_tran[j][i]]
                    self._om_dist(y_tran_index)

        else:
            self._om_dist(y_int)

    def _om_pair_dist(self, seq1, seq2):
        '''
        Method for calculating the optimal matching distance between a pair of
        sequences given a substitution cost matrix and an indel cost.

        Arguments
        ---------
        seq1            : array
                          (t1, ), the first sequence
        seq2            : array
                          (t2, ), the second sequence

        Returns
        -------
        D               : array
                          (t2+1, t1+1), score matrix: D[i+1,j+1] is the best
                          score for aligning the substring, seq1[0:j] and seq2[0:i],
                          and D[t2+1, t1+1] (or D[-1,-1]) is the global optimal score.

        '''
        return om_pair_dist(seq1, seq2, self.subs_mat, self.indel)
        # t1 = len(seq1)
        # t2 = len(seq2)
        #
        # D = np.zeros((t2 + 1, t1 + 1))
        # for j in range(1, t1 + 1):
        #     D[0, j] = self.indel * j
        # for i in range(1, t2 + 1):
        #     D[i, 0] = self.indel * i
        #
        # for i in range(1, t2 + 1):
        #     for j in range(1, t1 + 1):
        #         gaps = D[i, j - 1] + self.indel
        #         gapt = D[i - 1, j] + self.indel
        #         match = D[i - 1, j - 1] + self.subs_mat[
        #             seq1[j - 1], seq2[i - 1]]
        #         D[i, j] = min(match, gaps, gapt)
        # return D

    def _om_dist(self, y_int):
        '''
        Method for calculating optimal matching distances between all
        sequence pairs.

        Arguments
        ---------
        y_int           : array
                          Encoded longitudinal data ready for optimal matching.

        Note
        ----
        This method is optimized to calculate the distance between unique
        sequences only in order to save computation time.

        '''
        y_str = []
        for i in y_int:
            y_str.append(''.join(list(map(str, i))))

        moves_str, unique_indices = np.unique(y_str, axis=0, return_index=True)
        moves_int = y_int[unique_indices]
        uni_num = len(moves_str)
        dict_move_index = dict(zip(map(tuple, moves_int), range(uni_num)))

        # dict_move_index = dict(zip(map(tuple, moves_str), range(uni_num)))

        # y_uni = moves_int
        uni_seq_dis_mat = np.zeros((uni_num, uni_num))
        for pair in itertools.combinations(range(uni_num), 2):
            seq1 = moves_int[pair[0]]
            seq2 = moves_int[pair[1]]
            uni_seq_dis_mat[pair[0], pair[1]] = self._om_pair_dist(seq1,
                                                                   seq2)[-1, -1]
        uni_seq_dis_mat = uni_seq_dis_mat + uni_seq_dis_mat.transpose()

        seq_dis_mat = np.zeros((self.n, self.n))
        for pair in itertools.combinations(range(self.n), 2):
            seq1 = y_int[pair[0]]
            seq2 = y_int[pair[1]]
            seq_dis_mat[pair[0], pair[1]] = uni_seq_dis_mat[
                dict_move_index[tuple(seq1)],
                dict_move_index[tuple(seq2)]]

        self.seq_dis_mat = seq_dis_mat + seq_dis_mat.transpose()
