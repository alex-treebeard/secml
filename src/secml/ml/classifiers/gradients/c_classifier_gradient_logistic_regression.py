"""
.. module:: CClassifierGradientLinear
   :synopsis: Common interface for the implementations of the logistic
   regression classifier gradients

.. moduleauthor:: Ambra Demontis <ambra.demontis@diee.unica.it>
"""

from secml.array import CArray
from secml.ml.classifiers.gradients import CClassifierGradientLinear
from secml.ml.classifiers.loss import CLossLogistic
from secml.ml.classifiers.regularizer import CRegularizerL2
from secml.ml.classifiers.clf_utils import convert_binary_labels


class CClassifierGradientLogisticRegression(CClassifierGradientLinear):
    class_type = 'logistic'

    def __init__(self):
        self._loss = CLossLogistic()
        self._reg = CRegularizerL2()

    def _sigm(self, y, s):
        """
        Sigmoid function
        """
        y = CArray(y)
        s = CArray(s)
        return 1.0 / (1.0 + (-y * s).exp())

    def hessian(self, x, y, clf):
        """
        Compute hessian of the loss w.r.t. the classifier parameters
        """
        y = y.ravel()
        y = convert_binary_labels(y)
        y = CArray(y).astype(float).T  # column vector

        C = clf.C

        x = x.atleast_2d()
        n = x.shape[0]
        d = x.shape[1]

        # nb: we compute the score before the x normalization as decision
        # function normalizes x
        s = clf.decision_function(x, y=1).T
        sigm = self._sigm(y, s)
        z = sigm * (1 - sigm)

        # handle normalizer, if present
        x = x if clf.preprocess is None else clf.preprocess.normalize(x)

        # first derivative wrt b derived w.r.t. w
        diag = z * CArray.eye(n_rows=n, n_cols=n)
        dww = C * (x.T.dot(diag).dot(x)) + CArray.eye(d, d)  # matrix d*d
        dbw = C * ((z * x).sum(axis=0)).T  # column vector
        dbb = C * (z.sum(axis=None))  # scalar

        H = CArray.zeros((d + 1, d + 1))
        H[:d, :d] = dww
        H[:-1, d] = dbw
        H[d, :-1] = dbw.T
        H[-1, -1] = dbb

        return H
