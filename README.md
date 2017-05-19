# Sudoku Solver Bot

A Telegram bot that recognize a sudoku scheme, solves it and returns the image with the results

By Pinter.


## Modules

- `digitsDetector.py`: reads a digit from an image
- `solverLogic.py`: sudoku solver logic and solution formatter
- `sudokuSolver.py`: reads the sudoku from the image and returns the resulting image
- `sudokusolver_bot.py`: bot main, gets and sends messages and photos via Telegram

### Training Data

Training data files:
- `data/samples.npy`: contains a numpy float32 array of 20x20 px images.
- `data/labels.npy`: contains a numpy array of integers corresponding to each image in the samples file.


## Credits

This project uses:

- OpenCV 3.2.0 (3-clause BSD License): http://opencv.org/license.html
- telepot - Python framework for Telegram Bot API (MIT License): https://github.com/nickoala/telepot/blob/master/LICENSE.md


## References

- http://docs.opencv.org/3.2.0/index.html
- http://norvig.com/sudoku.html
- http://opencvpython.blogspot.it/2012/06/sudoku-solver-part-2.html
- https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/
