class SolverLogic:
    def __init__(self):
        self.digits = '123456789'
        self.rows = 'ABCDEFGHI'
        self.sols = self.digits
        self.squares = self._cross(self.rows, self.sols)
        self.unitlist = ([self._cross(self.rows, c) for c in self.sols] +
                         [self._cross(r, self.sols) for r in self.rows] +
                         [self._cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI')
                          for cs in ('123', '456', '789')])
        self.units = dict((s, [u for u in self.unitlist if s in u])
                          for s in self.squares)
        self.peers = dict((s, set(sum(self.units[s], [])) - set([s]))
                          for s in self.squares)

    def _cross(self, A, B):
        """ cross product of elements in A and elements in B. """
        return [a + b for a in A for b in B]

    def _parse_grid(self, grid):
        """convert grid to a dict of possible values, {square: digits},
        or return False if a contradiction is detected.
        """
        # To start, every square can be any digit;
        # then assign values from the grid
        values = dict((s, self.digits) for s in self.squares)
        for s, d in self.grid_values(grid).items():
            if d in self.digits and not self._assign(values, s, d):
                return False  # (Fail if we can't assign d to square s.)
        return values

    def _assign(self, values, s, d):
        """ eliminate all the values except d from values[s] and propagate.
        Return values, except return False if a contradiction is detected. """
        other_values = values[s].replace(d, '')
        if all(self._eliminate(values, s, d2) for d2 in other_values):
            return values
        else:
            return False

    def _eliminate(self, values, s, d):
        """ eliminate d from values[s]; propagate when values or places <= 2.
        Return values, except return False if a contradiction is detected.
        """
        if d not in values[s]:
            return values  # Already eliminated
        values[s] = values[s].replace(d, '')
        # (1) If a square s is reduced to one value d2,
        # then eliminate d2 from the self.peers.
        if len(values[s]) == 0:
            return False  # Contradiction: removed last value
        elif len(values[s]) == 1:
            d2 = values[s]
            if not all(self._eliminate(values, s2, d2)
                       for s2 in self.peers[s]):
                return False
        # (2) If a unit u is reduced to only one place for a value d,
        # then put it there.
        for u in self.units[s]:
            dplaces = [s for s in u if d in values[s]]
        if len(dplaces) == 0:
            return False  # Contradiction: no place for this value
        elif len(dplaces) == 1:
            # d can only be in one place in unit; self._assign it there
            if not self._assign(values, dplaces[0], d):
                return False
        return values

    def _search(self, values):
        """ using depth-first search and propagation,
        try all possible values.
        """
        if values is False:
            return False  # Failed earlier
        if all(len(values[s]) == 1 for s in self.squares):
            return values  # Solved!
        # Chose the unfilled square s with the fewest possibilities
        n, s = min((len(values[s]), s)
                   for s in self.squares if len(values[s]) > 1)
        return self._some(self._search(self._assign(values.copy(), s, d))
                          for d in values[s])

    def _some(self, seq):
        """ return some element of seq that is true. """
        for e in seq:
            if e:
                return e
        return False

    def grid_values(self, grid):
        """ convert grid into a dict of with '0' for empties. """
        chars = [c for c in grid if c in self.digits or c in '0.']
        assert len(chars) == 81
        return dict(zip(self.squares, chars))

    def solve(self, grid):
        solution = self._search(self._parse_grid(grid))
        if solution is False:
            solution = self.grid_values(grid)
        return solution
