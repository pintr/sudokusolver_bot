import cv2
import numpy as np
import string

from solverLogic import SolverLogic
from digitsDetector import DigitsDetector

BORDER_SIZE = 4
CELL_SIZE = 20
SCHEME_SIZE = (CELL_SIZE + 2 * BORDER_SIZE) * 9
DIGIT_MIN_AREA = (CELL_SIZE * CELL_SIZE) // CELL_SIZE


class SudokuSolver:
    def _biggest_contour(self, img):
        """ get the biggest contour in img """
        # get all the contours of segm
        _, cnts, _ = cv2.findContours(img, cv2.RETR_TREE,
                                      cv2.CHAIN_APPROX_SIMPLE)
        # get the biggest contour in image (the sudoku one)
        areaMax = 0
        cntMax = None
        for cnt in cnts:
            area = cv2.contourArea(cnt)
            if area > 100:
                per = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02 * per, True)
                if area > areaMax:
                    areaMax = area
                    cntMax = approx
        return areaMax, cntMax

    def _cells(self, warp):
        """ slice warped image in 81 blocks without borders """
        cells = np.array([np.hsplit(row, 9) for row in np.vsplit(warp, 9)])
        cells = cells.reshape(81, SCHEME_SIZE //
                              9, SCHEME_SIZE // 9)
        cells = [cell[BORDER_SIZE:(SCHEME_SIZE // 9 - BORDER_SIZE),
                      BORDER_SIZE:(SCHEME_SIZE // 9 - BORDER_SIZE)]
                 for cell in cells]
        return cells

    def _digits(self, cells):
        """ recognize digits in each cell """
        digitsDetector = DigitsDetector()
        digits = [0 for i in range(81)]

        for i in range(81):
            cell = cells[i]
            _, contours, _ = cv2.findContours(
                cell.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) > 0:
                largestContour = contours[np.argmax(
                    map(cv2.contourArea, contours))]
                if cv2.contourArea(largestContour) >= DIGIT_MIN_AREA:
                    digits[i] = digitsDetector.read_digit(cell, CELL_SIZE)

        return digits

    def _printable(self, digits, solution):
        string = ''
        for i, value in enumerate(solution.values()):
            res = int(value) - int(digits[i])
            if res not in {0, int(value)}:
                return False
            string += str(res)
        return string

    def _reorder(self, cnt):
        """ order the square points of the contour """
        # remove all single dimensional subsets
        squeezed = np.squeeze(cnt)
        reordered = np.zeros((4, 2), dtype=np.float32)
        rowsSum = squeezed.sum(axis=1)
        rowsDiff = np.diff(squeezed, axis=1)
        reordered[0] = squeezed[np.argmin(rowsSum)]   # top left angle
        reordered[1] = squeezed[np.argmax(rowsDiff)]  # bottom left angle
        reordered[2] = squeezed[np.argmax(rowsSum)]   # bottom right angle
        reordered[3] = squeezed[np.argmin(rowsDiff)]  # top right angle
        return reordered

    def _segmentize(self, img):
        """ segmentize image to identify the parts from which is composed """
        # adigitsDetector gaussian blur to help identifying edges
        blur = cv2.GaussianBlur(img, (5, 5), 0)
        # convert image to grayscale
        gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)
        # use adaptive threshold to convert image to binary image
        thresh = cv2.adaptiveThreshold(gray, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV, 11, 2)
        return thresh

    def _solution(self, digits):
        scheme = ''.join(str(d) for d in digits)
        logic = SolverLogic()
        solution = logic.solve(scheme)
        toprint = logic.grid_values(self._printable(digits, solution))
        return solution, toprint

    def _virtual_image(self, img, scheme):
        """ output known sudoku values to the real image """
        virtualImage = img.copy()
        size = 0.6
        for key, val in scheme.items():
            x = BORDER_SIZE + (int(key[1]) - 1) * (CELL_SIZE + 2 * BORDER_SIZE)
            y = (string.ascii_uppercase.index(
                key[0]) + 1) * (3 + CELL_SIZE + BORDER_SIZE)
            if val not in '0':
                cv2.putText(virtualImage, val,
                            (x, y), 0, size, (0, 255, 0))
        return virtualImage

    def _warp(self, cntOrd, segm):
        """ transform the segmentized image
        to 2D quadrangle vertices sudoku scheme
        """
        # initialize the resulting array
        resArray = np.float32([[0, 0], [0, SCHEME_SIZE],
                               [SCHEME_SIZE, SCHEME_SIZE], [SCHEME_SIZE, 0]])
        # get the perspective transform with quadrangle vertices
        perspective = cv2.getPerspectiveTransform(np.float32(cntOrd),
                                                  resArray)
        # apply the perspective transformation to segm
        scheme = cv2.warpPerspective(segm, perspective,
                                     (SCHEME_SIZE, SCHEME_SIZE))
        return scheme

    def solve(self, image):
        """ provide the scheme array from image """
        # image load as colored image
        img = cv2.imread(image, 1)
        # image segmentization
        segm = self._segmentize(img)
        # biggest contour and its area
        areaMax, cntMax = self._biggest_contour(segm)
        # square points of the contour
        cntOrd = self._reorder(cntMax)
        # 2D transformation of the segmentized image
        warp = self._warp(cntOrd, segm)
        # the 81 cells of sudoku
        cells = self._cells(warp)
        # digits in every cell
        digits = self._digits(cells)
        # check if the sudoku is solvabe
        if digits.count(0) > 64:
            return False
        # solve the sudoku from the digits grid
        solution, toprint = self._solution(digits)
        # Add the digits to original image
        virtualImage = self._virtual_image(self._warp(cntOrd, img), toprint)
        return virtualImage
