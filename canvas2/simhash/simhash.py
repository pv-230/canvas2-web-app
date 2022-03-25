from collections import Counter
import numpy as np

def parseText(inputFile: str) -> list:
    """
    Parse text file and return a list of words
    Ignore any non-alphanumeric characters
    """
    with open(inputFile, 'r') as f:
        words = f.read().split()
        words = [word.lower() for word in words if word.isalnum()]
    return words

def getWordFrequencies(words: list) -> Counter:
    """
    Return a Counter object with word frequencies
    """
    return Counter(words)

def getHash(inputFile: str) -> int:
    words = parseText(inputFile)
    wordFrequencies = getWordFrequencies(words)

    wordHash = dict()
    for word in wordFrequencies.keys():
        wordHash[word] = [int(x) * wordFrequencies[word] if int(x) == 1 else -1 for x in bin(sum(ord(c) for c in word))[2:].zfill(12)]

    sumHash = np.array(list(wordHash.values()))
    sumHash = np.sum(sumHash, axis=0)
    
    sumHash = ''.join(['1' if x > 0 else '0' for x in sumHash])
    return sumHash


    
   

print(getHash('doc1.txt'))
print(getHash('doc1similar.txt'))

    
    