from math import sqrt, ceil
import unittest

import numpy as np

try:
    import cupy as cp
except:
    cp = np
    print("WARNING: CuPy could not be imported!")

from minisom import MiniSom

from xpysom_dask import XPySom
from xpysom_dask.distances import (
    cosine_distance,
    manhattan_distance,
    euclidean_squared_distance,
)
from xpysom_dask.neighborhoods import (
    gaussian_generic,
    gaussian_rect,
    mexican_hat_generic,
    mexican_hat_rect,
    bubble,
    triangle,
    prepare_neig_func,
)

import pickle
import os


class TestCupySom(unittest.TestCase):
    def setUp(self, xp=np):
        self.xp = xp
        self.som = XPySom(5, 5, 1, std_coeff=1, xp=xp)
        self.minisom = MiniSom(5, 5, 1)

        for i in range(5):
            for j in range(5):
                # checking weights normalization
                np.testing.assert_almost_equal(
                    1.0, np.linalg.norm(self.som.weights[i, j])
                )
        self.som.weights = np.zeros((5, 5, 1))  # fake weights
        self.som.weights[2, 3] = 5.0
        self.som.weights[1, 1] = 2.0

        np.random.seed(1234)

        if self.xp.__name__ == "cupy":
            cp.random.seed(1234)

    def test_unavailable_neigh_function(self):
        with self.assertRaises(ValueError):
            XPySom(5, 5, 1, neighborhood_function="boooom")

    def test_unavailable_distance_function(self):
        with self.assertRaises(ValueError):
            XPySom(5, 5, 1, activation_distance="ridethewave")

    def test_win_map(self):
        winners = self.som.win_map([[5.0], [2.0]])
        assert winners[(2, 3)][0] == [5.0]
        assert winners[(1, 1)][0] == [2.0]

    def test_labels_map(self):
        labels_map = self.som.labels_map([[5.0], [2.0]], ["a", "b"])
        assert labels_map[(2, 3)]["a"] == 1
        assert labels_map[(1, 1)]["b"] == 1
        with self.assertRaises(ValueError):
            self.som.labels_map([[5.0]], ["a", "b"])

    def test_activation_reponse(self):
        response = self.som.compute_populations([[5.0], [2.0]])
        assert response[2, 3] == 1
        assert response[1, 1] == 1

    def test_activate(self):
        assert self.som.activate(5.0).argmin() == 13.0  # unravel(13) = (2,3)

    def test_distance_from_weights(self):
        data = np.arange(-5, 5).reshape(-1, 1)
        weights = self.som.weights.reshape(-1, self.som.weights.shape[2])
        distances = self.som.distance_from_weights(data, weights)
        for i in range(len(data)):
            for j in range(len(weights)):
                assert distances[i][j] == np.linalg.norm(data[i] - weights[j])

    def test_quantization_error(self):
        assert self.som.quantization_error([[5], [2]]) == 0.0
        assert self.som.quantization_error([[4], [1]]) == 1.0

    def test_topographic_error(self):
        # 5 will have bmu_1 in (2,3) and bmu_2 in (2, 4)
        # which are in the same neighborhood
        self.som.weights[2, 4] = 6.0
        # 15 will have bmu_1 in (4, 4) and bmu_2 in (0, 0)
        # which are not in the same neighborhood
        self.som.weights[4, 4] = 15.0
        self.som.weights[0, 0] = 14.0
        assert self.som.topographic_error([[5]]) == 0.0
        assert self.som.topographic_error([[15]]) == 1.0

    def test_quantization(self):
        q = self.som.quantization(np.array([[4], [2]]))
        assert q[0] == 5.0
        assert q[1] == 2.0

    def test_random_seed(self):
        som1 = XPySom(5, 5, 2, sigma=1.0, learning_rate=0.5, random_seed=1)
        som2 = XPySom(5, 5, 2, sigma=1.0, learning_rate=0.5, random_seed=1)
        # same initialization
        np.testing.assert_array_almost_equal(som1.weights, som2.weights)
        data = np.random.rand(100, 2)
        som1 = XPySom(5, 5, 2, sigma=1.0, learning_rate=0.5, random_seed=1)
        som1.train_random(data, 10)
        som2 = XPySom(5, 5, 2, sigma=1.0, learning_rate=0.5, random_seed=1)
        som2.train_random(data, 10)
        # same state after training
        np.testing.assert_array_almost_equal(som1.weights, som2.weights)

    def test_train(self):
        som = XPySom(5, 5, 2, sigma=1.0, learning_rate=0.5, random_seed=1)
        data = np.array([[4, 2], [3, 1]])
        q1 = som.quantization_error(data)
        som.train(data, 10)
        assert q1 > som.quantization_error(data)

        data = np.array([[1, 5], [6, 7]])
        q1 = som.quantization_error(data)
        som.train(data, 10, verbose=True)
        assert q1 > som.quantization_error(data)

    def test_random_weights_init(self):
        som = XPySom(2, 2, 2, random_seed=1)
        som.random_weights_init(np.array([[1.0, 0.0]]))
        for w in som.weights:
            np.testing.assert_array_equal(w[0], np.array([1.0, 0.0]))

    def test_pca_weights_init(self):
        som = XPySom(2, 2, 2)
        som.pca_weights_init(np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 0.0], [0.0, 1.0]]))
        expected = np.array(
            [
                [[0.0, -1.41421356], [-1.41421356, 0.0]],
                [[1.41421356, 0.0], [0.0, 1.41421356]],
            ]
        )
        np.testing.assert_array_almost_equal(som.weights, expected)

    def test_distance_map(self):
        som = XPySom(2, 2, 2, random_seed=1)
        som.weights = np.array([[[1.0, 0.0], [0.0, 1.0]], [[1.0, 0.0], [0.0, 1.0]]])
        np.testing.assert_array_equal(
            som.distance_map(), np.array([[1.0, 1.0], [1.0, 1.0]])
        )

        som = MiniSom(2, 2, 2, topology="hexagonal", random_seed=1)
        som._weights = np.array([[[1.0, 0.0], [0.0, 1.0]], [[1.0, 0.0], [0.0, 1.0]]])
        np.testing.assert_array_equal(
            som.distance_map(), np.array([[0.5, 1.0], [1.0, 0.5]])
        )

    def test_pickling(self):
        with open("som.p", "wb") as outfile:
            pickle.dump(self.som, outfile)
        with open("som.p", "rb") as infile:
            pickle.load(infile)
        os.remove("som.p")

    def test_euclidean_distance(self):
        x = np.random.rand(100, 20)
        w = np.random.rand(10, 10, 20)
        w_flat = w.reshape(-1, w.shape[2])
        cs_dist = euclidean_squared_distance(
            self.xp.array(x), self.xp.array(w_flat), xp=self.xp
        )
        if self.xp.__name__ == "cupy":
            cs_dist = cp.asnumpy(cs_dist)
        cs_dist = cs_dist.reshape((100, 10, 10))
        for i, sample in enumerate(x):
            ms_dist = self.minisom._euclidean_distance(sample, w) ** 2
            np.testing.assert_array_almost_equal(ms_dist, cs_dist[i])

    def test_cosine_distance(self):
        x = np.random.rand(100, 20)
        w = np.random.rand(10, 10, 20)
        w_flat = w.reshape(-1, w.shape[2])
        cs_dist = cosine_distance(self.xp.array(x), self.xp.array(w_flat), xp=self.xp)
        if self.xp.__name__ == "cupy":
            cs_dist = cp.asnumpy(cs_dist)
        cs_dist = cs_dist.reshape((100, 10, 10))
        for i, sample in enumerate(x):
            ms_dist = self.minisom._cosine_distance(sample, w)
            np.testing.assert_array_almost_equal(ms_dist, cs_dist[i])

    def test_manhattan_distance(self):
        x = np.random.rand(100, 20)
        w = np.random.rand(10, 10, 20)
        w_flat = w.reshape(-1, w.shape[2])
        cs_dist = manhattan_distance(
            self.xp.array(x), self.xp.array(w_flat), xp=self.xp
        )
        if self.xp.__name__ == "cupy":
            cs_dist = cp.asnumpy(cs_dist)
        cs_dist = cs_dist.reshape((100, 10, 10))
        for i, sample in enumerate(x):
            ms_dist = self.minisom._manhattan_distance(sample, w)
            np.testing.assert_array_almost_equal(ms_dist, cs_dist[i])

    def test_gaussian(self):
        cx, cy = self.xp.meshgrid(self.xp.arange(5), self.xp.arange(5))
        c = (cx.flatten(), cy.flatten())

        cs_gauss = gaussian_rect(
            self.som._neigx,
            self.som._neigy,
            self.som._std_coeff,
            False,
            c,
            1,
            xp=self.xp,
        )

        if self.xp.__name__ == "cupy":
            cs_gauss = cp.asnumpy(cs_gauss)

        for i in range(len(c[0])):
            x = c[0][i].item()
            y = c[1][i].item()
            ms_gauss = self.minisom._gaussian((x, y), 1)
            np.testing.assert_array_almost_equal(ms_gauss, cs_gauss[i])

    def test_mexican_hat(self):
        cx, cy = self.xp.meshgrid(self.xp.arange(5), self.xp.arange(5))
        c = (cx.flatten(), cy.flatten())

        cs_mex = mexican_hat_rect(
            self.som._neigx,
            self.som._neigy,
            self.som._std_coeff,
            False,
            c,
            1,
            xp=self.xp,
        )

        if self.xp.__name__ == "cupy":
            cs_mex = cp.asnumpy(cs_mex)

        for i in range(len(c[0])):
            x = c[0][i].item()
            y = c[1][i].item()
            ms_mex = self.minisom._mexican_hat((x, y), 1)
            np.testing.assert_array_almost_equal(ms_mex, cs_mex[i])

    def test_bubble(self):
        cx, cy = self.xp.meshgrid(self.xp.arange(5), self.xp.arange(5))
        c = (cx.flatten(), cy.flatten())

        cs_bub = bubble(self.som._neigx, self.som._neigy, c, 1, xp=self.xp)

        if self.xp.__name__ == "cupy":
            cs_bub = cp.asnumpy(cs_bub)

        for i in range(len(c[0])):
            x = c[0][i].item()
            y = c[1][i].item()
            ms_bub = self.minisom._bubble((x, y), 1)
            np.testing.assert_array_almost_equal(ms_bub, cs_bub[i])

    def test_triangle(self):
        cx, cy = self.xp.meshgrid(self.xp.arange(5), self.xp.arange(5))
        c = (cx.flatten(), cy.flatten())

        cs_tri = triangle(self.som._neigx, self.som._neigy, False, c, 1, xp=self.xp)

        if self.xp.__name__ == "cupy":
            cs_tri = cp.asnumpy(cs_tri)

        for i in range(len(c[0])):
            x = c[0][i].item()
            y = c[1][i].item()
            ms_tri = self.minisom._triangle((x, y), 1)
            np.testing.assert_array_almost_equal(ms_tri, cs_tri[i])


class TestNumpySom(TestCupySom):
    def setUp(self):
        TestCupySom.setUp(self, xp=np)


class TestCupySomHex(unittest.TestCase):
    def setUp(self, xp=np):
        self.xp = xp
        self.som = XPySom(5, 5, 1, topology="hexagonal", std_coeff=1, xp=xp)
        self.minisom = MiniSom(5, 5, 1, topology="hexagonal")

        for i in range(5):
            for j in range(5):
                # checking weights normalization
                np.testing.assert_almost_equal(
                    1.0, np.linalg.norm(self.som.weights[i, j])
                )
        self.som.weights = np.zeros((5, 5, 1))  # fake weights
        self.som.weights[2, 3] = 5.0
        self.som.weights[1, 1] = 2.0

        np.random.seed(1234)

        if self.xp.__name__ == "cupy":
            cp.random.seed(1234)

    def test_gaussian(self):
        cx, cy = self.xp.meshgrid(self.xp.arange(5), self.xp.arange(5))
        c = (cx.flatten(), cy.flatten())

        cs_gauss = gaussian_generic(
            self.som._xx, self.som._yy, self.som._std_coeff, False, c, 1, xp=self.xp
        )

        if self.xp.__name__ == "cupy":
            cs_gauss = cp.asnumpy(cs_gauss)

        for i in range(len(c[0])):
            x = c[0][i].item()
            y = c[1][i].item()
            ms_gauss = self.minisom._gaussian((x, y), 1)
            np.testing.assert_array_almost_equal(ms_gauss, cs_gauss[i])

    def test_mexican_hat(self):
        cx, cy = self.xp.meshgrid(self.xp.arange(5), self.xp.arange(5))
        c = (cx.flatten(), cy.flatten())

        cs_mex = mexican_hat_generic(
            self.som._xx, self.som._yy, self.som._std_coeff, False, c, 1, xp=self.xp
        )

        if self.xp.__name__ == "cupy":
            cs_mex = cp.asnumpy(cs_mex)

        for i in range(len(c[0])):
            x = c[0][i].item()
            y = c[1][i].item()
            ms_mex = self.minisom._mexican_hat((x, y), 1)
            np.testing.assert_array_almost_equal(ms_mex, cs_mex[i])

    def test_bubble(self):
        cx, cy = self.xp.meshgrid(self.xp.arange(5), self.xp.arange(5))
        c = (cx.flatten(), cy.flatten())

        cs_bub = bubble(self.som._neigx, self.som._neigy, c, 1, xp=self.xp)

        if self.xp.__name__ == "cupy":
            cs_bub = cp.asnumpy(cs_bub)

        for i in range(len(c[0])):
            x = c[0][i].item()
            y = c[1][i].item()
            ms_bub = self.minisom._bubble((x, y), 1)
            np.testing.assert_array_almost_equal(ms_bub, cs_bub[i])


class TestNumpySomHex(TestCupySomHex):
    def setUp(self):
        TestCupySom.setUp(self, xp=np)
