from collections import Counter
from nltk import tokenize
import numpy as np


def parseTextFile(inputFile: str) -> list:
    """
    Parse text file and return a list of sentences
    """
    with open(inputFile, 'r') as f:
        text = f.read()
        text = tokenize.sent_tokenize(text)

    tkn = tokenize.TweetTokenizer()
    text = [tkn.tokenize(sent) for sent in text]
    return text


def parseText(inputText: str) -> list:
    """
    Parse text file and return a list of sentences
    """
    text = tokenize.sent_tokenize(inputText)
    text = [tokenize.word_tokenize(sent) for sent in text]
    return text


def getWordFrequencies(words: list) -> Counter:
    """
    Return a Counter object with word frequencies
    """
    return Counter(words)


def strHash(s: str) -> bin:
    """
    Return a binary hash of a string as the sum of two polynomial rolling hashes
    """
    return hashFunction(s, 31) + hashFunction(s, 41)


def hashFunction(s: str, seed: int) -> str:
    """
    Return a hash of a string via a polynomial rolling hash function given a seed
    Source: this hash function was inspired by https://cp-algorithms.com/string/string-hashing.html (translated from C++)
    """
    hashVal = 0
    p = 1
    for c in s:
        hashVal = (hashVal + (ord(c) - ord('a') + 1) * p) % 1000003
        p = (p * seed) % 1000003
    return bin(hashVal)[2:].zfill(20)


def getSentenceHash(sentence: str) -> int:
    """
    Return a hash of a sentence
    Source: hashing technique from https://www.youtube.com/watch?v=gnraT4N43qo (just idea not implementation)
    """
    wordFrequencies = getWordFrequencies(sentence)

    wordHash = dict()
    for word in wordFrequencies.keys():
        wordHash[word] = [int(x) * wordFrequencies[word]
                          if int(x) == 1 else -1 for x in strHash(word)]

    sumHash = np.array(list(wordHash.values()))
    sumHash = np.sum(sumHash, axis=0)

    sumHash = ''.join(['1' if x > 0 else '0' for x in sumHash])
    return sumHash


def getHash(parsedText: list) -> list:
    """
    Return a list of hashes of each sentence
    """
    hashes = []

    for i, sentence in enumerate(parsedText):
        hashes.append((i + 1, getSentenceHash(sentence)))
    return hashes


def getStringDifference(s1: str, s2: str) -> int:
    """
    Return the number of chars that are different between two strings
    """
    return sum(x != y for x, y in zip(s1, s2))


def getSimilarSentences(hash1: list, hash2: list, k=8) -> list:
    """
    Return a list of sentences that are similar to the input sentence
    """
    similarSentences = []
    paired1, paired2 = set(), set()

    # iterate through first hash set and if a hash with a difference of i is found in the other set
    # create a pair and move to next sentence do this for all i in range(k)
    for i in range(0, k + 1):
        for idx, sentenceHash in hash1:
            if idx not in paired1:
                for idx2, sentenceHash2 in hash2:
                    if idx2 not in paired2:
                        currDiff = getStringDifference(
                            sentenceHash, sentenceHash2)
                        if currDiff == i:
                            similarSentences.append((idx, idx2))
                            paired1.add(idx)
                            paired2.add(idx2)
                            break
    return similarSentences


def getLCS(s1: list, s2: list) -> list:
    """
    Return all common subsequences between two lists of words
    """
    s1 = " ".join([x.lower() for x in s1 if x.isalnum()])
    s2 = " ".join([x.lower() for x in s2 if x.isalnum()])

    # find the longest common substring between st1 and st2
    def helperLCS(st1, st2):
        # create an array of starting indicies of words so partial words matches are not considered
        startIdxs = [0]
        for i in range(len(st1)):
            if i > 0 and st1[i-1] == ' ':
                startIdxs.append(i)
        startIdxs.append(len(st1))

        # iterate over the start indicies and find the longest substring that has a match
        longest = ""
        for i in range(len(startIdxs)):
            for j in range(i+1, len(startIdxs)):
                curr = st1[startIdxs[i]:startIdxs[j]]
                if curr in st2:
                    if len(curr) > len(longest):
                        longest = curr
        return longest

    # find the LCS then remove it from the strings and repeat until no LCS is found
    commonSubsequences = []
    while helperLCS(s1, s2) != "":
        curr = helperLCS(s1, s2)
        s1 = s1.replace(curr, "", 1)
        s2 = s2.replace(curr, "", 1)
        curr = curr.rstrip()
        if (curr.count(' ')) >= 2:
            commonSubsequences.append(curr)

    return commonSubsequences


def getCommonSubstrings(text1: list, text2: list) -> str:
    """
    Return a string representation of a set of shingles
    """
    hash1 = getHash(text1)
    hash2 = getHash(text2)

    similarSentences = getSimilarSentences(hash1, hash2)
    return similarSentences