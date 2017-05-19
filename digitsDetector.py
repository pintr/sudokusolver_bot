import cv2
import numpy as np
from numpy.linalg import norm

CELL_SIZE = 20
KNN_K = 13
KNN_LABELS = "data/labels.npy"
KNN_SAMPLES = "data/samples.npy"


class DigitsDetector:
    def __init__(self):
        """ Prepare and train knn. """
        _samples = np.load(KNN_SAMPLES)
        self.samples = self._preprocess(_samples, CELL_SIZE)
        self.labels = np.load(KNN_LABELS).astype(int)
        self.knn = cv2.ml.KNearest_create()
        self.knn.train(self.samples, cv2.ml.ROW_SAMPLE, self.labels)
        self.iterations = [-1, 0, 1, 2]
        self.lvl = 0  # index of .iterations

    def _deskew(self, img, cellSize):
        """ deskew each sample image."""
        m = cv2.moments(img)
        if np.abs(m['mu02']) < 1e-2:
            return img.copy()
        skew = m['mu11'] / m['mu02']
        M = np.float32([[1, skew, -0.5 * cellSize * skew], [0, 1, 0]])
        img = cv2.warpAffine(img, M, (cellSize, cellSize),
                             flags=cv2.WARP_INVERSE_MAP | cv2.INTER_LINEAR)
        return img

    def _hog(self, digits, cellSize):
        """ compute histogram-of-gradients for each sample image. """
        samples = []
        for img in digits:
            gx = cv2.Sobel(img, cv2.CV_32F, 1, 0)
            gy = cv2.Sobel(img, cv2.CV_32F, 0, 1)
            mag, ang = cv2.cartToPolar(gx, gy)
            bin_n = 16
            bin_ = np.int32(bin_n * ang / (2 * np.pi))
            bin_cells = bin_[:10, :10], bin_[
                10:, :10], bin_[:10, 10:], bin_[10:, 10:]
            mag_cells = mag[:10, :10], mag[10:,
                                           :10], mag[:10, 10:], mag[10:, 10:]
            hists = [np.bincount(b.ravel(), m.ravel(), bin_n)
                     for b, m in zip(bin_cells, mag_cells)]
            hist = np.hstack(hists)

            # transform to Hellinger kernel
            eps = 1e-7
            hist /= hist.sum() + eps
            hist = np.sqrt(hist)
            hist /= norm(hist) + eps
            samples.append(hist)
        return np.float32(samples)

    def _preprocess(self, img, cellSize):
        cells = np.float32(img).reshape(-1, cellSize, cellSize)
        deskewedSamples = [self._deskew(cell, cellSize) for cell in cells]

        return self._hog(deskewedSamples, cellSize)

    def read_digit(self, img, cellSize):
        """ read digit in img and returns int value """

        retval, results, neighborResponses, dists = self.knn.findNearest(
            self._preprocess(img, cellSize), KNN_K)

        return int(results.ravel()[0])
