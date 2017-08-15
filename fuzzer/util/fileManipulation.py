# -*- coding: utf-8 -*-
# reference Mozila Security funfuzz
from __future__ import absolute_import, print_function


def writeLinesToFile(lines, filename):
    """Write lines to a given filename."""
    with open(filename, 'wb') as f:
        f.writelines(lines)


def fuzzSplice(filename):
    """Return the lines of a file, minus the ones between the two lines containing SPLICE."""
    before = []
    after = []
    with open(filename, 'rb') as f:
        for line in f:
            before.append(line)
            if line.find("SPLICE") != -1:
                break
        for line in f:
            if line.find("SPLICE") != -1:
                after.append(line)
                break
        for line in f:
            after.append(line)
    return [before, after]


def linesStartingWith(lines, searchFor):
    """Return the lines from an array that start with a given string."""
    matchingLines = []
    for line in lines:
        if line.startswith(searchFor):
            matchingLines.append(line)
    return matchingLines