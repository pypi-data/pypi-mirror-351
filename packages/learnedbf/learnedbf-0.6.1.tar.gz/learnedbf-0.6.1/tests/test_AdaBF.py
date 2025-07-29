import unittest
import numpy as np
from learnedbf import AdaBF
from learnedbf.classifiers import ScoredRandomForestClassifier, ScoredMLP, \
    ScoredDecisionTreeClassifier, ScoredLinearSVC


class TestAdaBF(unittest.TestCase):

    def flip_bits(self, bit_mask, prob=0.1):
        mask = np.random.rand(bit_mask.shape[0]) > prob
        n_flipped = len(mask) - sum(mask)
        flipped_array = np.array([bit_mask[i] != 0 if p_ > prob \
                                   else not bit_mask[i]    
                                   for i,p_ in enumerate(mask)])
        return flipped_array, n_flipped
    
    @classmethod
    def setUpClass(cls):
        np.random.seed(42)
        print('set the pseudo-random seed to 42')

    def setUp(self):
        self.filters = [
            AdaBF(
                m=100, 
                classifier=ScoredDecisionTreeClassifier()),
            AdaBF(
                m=100, 
                classifier=ScoredMLP(max_iter=100000, activation='logistic')),
            AdaBF(m=100, 
                classifier=ScoredRandomForestClassifier()),
            AdaBF(m=100, 
                classifier=ScoredLinearSVC(max_iter=100000, tol=0.1, C=0.1))
        ]

        n_samples = 100
        Fn = 0.1
        Fp = 0.1
        self.objects = np.expand_dims(np.arange(0, n_samples*2), axis=1)
        labels_f, _ = self.flip_bits(np.array([False] * n_samples), Fn)
        labels_t, _ = self.flip_bits(np.array([True] * n_samples), Fp)
        self.labels = np.concatenate((labels_f, labels_t))

        for adabf in self.filters:
            adabf.fit(self.objects, self.labels)
        

    def test_fit(self):
        for adabf in self.filters:
            assert adabf.is_fitted_

        
    def test_FN(self):
        for adabf in self.filters:
            self.assertTrue(sum(adabf.predict(self.objects[~self.labels]) == 0))

if __name__ == '__main__':
    unittest.main()
