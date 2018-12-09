"""
.. module:: CClassifierNearestCentroid
   :synopsis: Nearest Centroid Classifier

.. moduleauthor:: Ambra Demontis <ambra.demontis@diee.unica.it>
.. moduleauthor:: Marco Melis <marco.melis@diee.unica.it>

"""
from secml.array import CArray
from secml.ml.classifiers import CClassifier
from secml.ml.classifiers.clf_utils import convert_binary_labels
from sklearn.neighbors import NearestCentroid
from sklearn.metrics import pairwise_distances


# TODO: EXPAND CLASS DOCSTRING
class CClassifierNearestCentroid(CClassifier):
    """CClassifierNearestCentroid."""
    __class_type = 'nrst_centroid'

    def __init__(self, metric='euclidean',
                 shrink_threshold=None, normalizer=None):

        # Calling CClassifier init
        super(CClassifierNearestCentroid, self).__init__(normalizer=normalizer)

        self._metric = metric
        self._shrink_threshold = shrink_threshold

        self._nc = None
        self._centroids = None

    def __clear(self):
        """Reset the object."""
        self._nc = None
        self._centroids = None

    def is_clear(self):
        """Returns True if object is clear."""
        return self._nc is None and self._centroids is None and \
            super(CClassifierNearestCentroid, self).is_clear()

    @property
    def metric(self):
        return self._metric

    @property
    def centroids(self):
        return self._centroids

    def _train(self, dataset):
        """Trains classifier 
    
        Parameters
        ----------
        dataset : CDataset
            Binary (2-class) training set. Must be a :class:`.CDataset`
            instance with patterns data and corresponding labels.

        Returns
        -------
        trained_cls : CClassifierKernelDensityEstimator
            Instance of the KDE classifier trained using input dataset.

        """
        if dataset.num_classes > 2:
            raise ValueError("training can be performed on (1-classes) or "
                             "binary datasets only. If dataset is binary only "
                             "negative class are considered.")

        self._nc = NearestCentroid(self._metric, self._shrink_threshold)

        self._nc.fit(dataset.X.get_data(), dataset.Y.tondarray())

        self._centroids = CArray(self._nc.centroids_)

        return self._nc

    def discriminant_function(self, x, y=1):
        """Computes the discriminant function for each pattern in x.

        The score is the distance of each pattern
         from the centroid of class `y`

        If a normalizer has been specified, input is normalized
         before computing the discriminant function.

        Parameters
        ----------
        x : CArray
            Array with new patterns to classify, 2-Dimensional of shape
            (n_patterns, n_features).
        y : {0, 1}, optional
            The label of the class wrt the function should be calculated.
            Default is 1.

        Returns
        -------
        score : CArray
            Value of the discriminant function for each test pattern.
            Dense flat array of shape (n_patterns,).

        """
        if self.is_clear():
            raise ValueError("make sure the classifier is trained first.")

        x = x.atleast_2d()  # Ensuring input is 2-D

        # Normalizing data if a normalizer is defined
        if self.normalizer is not None:
            x = self.normalizer.normalize(x)

        sign = convert_binary_labels(y)  # Sign depends on input label (0/1)

        return sign * self._discriminant_function(x)

    def _discriminant_function(self, x, y=1):
        """Computes the discriminant function for each pattern in x.

        The score is the distance of each pattern
         from the centroid of class `label`

        Parameters
        ----------
        x : CArray
            Array with new patterns to classify, 2-Dimensional of shape
            (n_patterns, n_features).
        y : {1}
            The label of the class wrt the function should be calculated.
            Discriminant function is always computed wrt positive class (1).

        Returns
        -------
        score : CArray
            Value of the discriminant function for each test pattern.
            Dense flat array of shape (n_patterns,).

        """
        if y != 1:
            raise ValueError(
                "discriminant function is always computed wrt positive class.")

        x = x.atleast_2d()  # Ensuring input is 2-D

        dist_from_ben_centroid = pairwise_distances(
            x.get_data(), self.centroids[0, :].atleast_2d().get_data(),
            metric=self.metric)
        dis_from_mal_centroid = pairwise_distances(
            x.get_data(), self.centroids[1, :].atleast_2d().get_data(),
            metric=self.metric)

        return CArray(
                dist_from_ben_centroid - dis_from_mal_centroid).ravel()
