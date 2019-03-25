from secml.ml.classifiers.tests import CClassifierTestCases

from io import open  # TODO: REMOVE AFTER TRANSITION TO PYTHON 3

from secml.pytorch.classifiers import CClassifierPyTorch
from secml.pytorch.models import mlp
from secml.data.loader import CDLRandom
from secml.utils import fm


class TestCClassifierPyTorch(CClassifierTestCases):

    def setUp(self):

        self.ds = CDLRandom(n_samples=100, n_classes=10,
                            n_features=20, n_informative=15,
                            random_state=0).load()

    def test_loaddict(self):
        """Test for model initialization from a file with params dict."""
        dict_file = fm.join(fm.abspath(__file__), 'mlp_params.txt')
        # Cleaning test file
        try:
            fm.remove_file(dict_file)
        except (OSError, IOError) as e:
            pass

        # Creating a textfile with model params
        mlp_params = {'input_dims': 20, 'output_dims': 10}
        with open(dict_file, 'wt', encoding='ascii') as df:
            for p in mlp_params:
                df.write(u'{:}: {:}\n'.format(p, mlp_params[p]))

        clf = CClassifierPyTorch(model=mlp, model_params=dict_file)

        self.logger.info("Model params:\n{:}".format(clf.model_params))
        self.assertEqual(mlp_params, clf.model_params)

        # Cleaning test file
        try:
            fm.remove_file(dict_file)
        except (OSError, IOError) as e:
            self.logger.info(e)


if __name__ == '__main__':
    CClassifierTestCases.main()
