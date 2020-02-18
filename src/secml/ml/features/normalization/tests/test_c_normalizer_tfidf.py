from secml.ml.features.tests import CPreProcessTestCases

from sklearn.feature_extraction.text import TfidfTransformer

from secml.array import CArray
from secml.ml.features.normalization import CNormalizerTfIdf


class TestCNormalizerTFIDF(CPreProcessTestCases):
    """Unittest for TestCNormalizerTFIDF."""

    def test_norm_minmax(self):
        """Test for TestCNormalizerTFIDF."""

        def sklearn_comp(array):

            self.logger.info("Original array is:\n{:}".format(array))

            # Sklearn normalizer (requires float dtype input)
            array_sk = array.astype(float).tondarray()
            sk_norm = TfidfTransformer().fit(array_sk)

            target = CArray(sk_norm.transform(array_sk))

            # Our normalizer
            our_norm = CNormalizerTfIdf().fit(array)
            result = our_norm.transform(array)

            self.logger.info("Correct result is:\n{:}".format(target))
            self.logger.info("Our result is:\n{:}".format(result))

            self.assert_array_almost_equal(target, result)

            # Testing out of range normalization

            self.logger.info("Testing out of range normalization")

            # Sklearn normalizer (requires float dtype input)
            target = CArray(sk_norm.transform(array_sk * 2))

            # Our normalizer
            result = our_norm.transform(array * 2)

            self.logger.info("Correct result is:\n{:}".format(target))
            self.logger.info("Our result is:\n{:}".format(result))

            self.assert_array_almost_equal(target, result)

        sklearn_comp(self.array_dense)
        sklearn_comp(self.array_sparse)
        sklearn_comp(self.row_dense.atleast_2d())
        sklearn_comp(self.row_sparse)
        sklearn_comp(self.column_dense)
        sklearn_comp(self.column_sparse)

    def test_chain(self):
        """Test a chain of preprocessors."""
        x_chain = self._test_chain(
            self.array_dense,
            ['min-max', 'pca', 'min-max'],
            [{'feature_range': (-5, 5)}, {}, {'feature_range': (0, 1)}]
        )

        # Expected shape is (3, 3), as pca max n_components is 4-1
        self.assertEqual((self.array_dense.shape[0],
                          self.array_dense.shape[1]-1), x_chain.shape)

    def test_chain_gradient(self):
        """Check gradient of a chain of preprocessors."""
        grad = self._test_chain_gradient(
            self.array_dense,
            ['tf-idf', 'mean-std', 'tf-idf'],
            [{'norm': 'l1'}, {}, {}]
        )

        # Expected shape is (n_feats, ), so (4, )
        self.assertEqual((self.array_dense.shape[1], ), grad.shape)


if __name__ == '__main__':
    CPreProcessTestCases.main()
