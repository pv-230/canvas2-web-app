import nltk
from nltk.stem import WordNetLemmatizer
from nltk import FreqDist
from nltk.corpus import brown

def parseText(inputFile: str) -> list:
    """
    Parse text file and return a list of words
    Ignore any non-alphanumeric characters
    Ignore any words that are among the 1000 most common words in English
    Words are lemmatized into their base form
    Resulting words get reduced to their most common synonym (this combats plagiarism by rewording)
    """

    ignoreThese = set()
    with open('mostCommonWords.txt', 'r') as f:
        for line in f:
            ignoreThese.add(line.strip())

    with open(inputFile, 'r') as f:
        words = f.read().split()
        words = [word.lower() for word in words if word.isalnum() and word.lower() not in ignoreThese]

    
    frequencyList = FreqDist(x.lower() for x in brown.words())
    words = [WordNetLemmatizer().lemmatize(word) for word in words]

    seen = dict()
    for i, word in enumerate(words):
        if word in seen:
            words[i] = seen[word]
        else:
            synonyms = set()
            for syn in nltk.corpus.wordnet.synsets(word):
                for l in syn.lemmas():
                    synonyms.add(l.name())
            stack = []
            for syn in synonyms:
                if not stack:
                    stack.append((syn, frequencyList[syn]))
                else:
                    if frequencyList[syn] > stack[-1][1]:
                        stack.pop()
                        stack.append((syn, frequencyList[syn]))
            if stack:
                words[i] = stack[0][0]
                seen[word] = stack[0][0]
    return words

def shingles(words: list, k: int) -> set:
    """
    Return a list of shingles of length k
    """
    words = " ".join(words)
    shingles = set()
    for i in range(len(words) - k + 1):
        shingles.add(''.join(words[i:i+k]))
    return shingles

def similarityScore(shingle1: set, shingle2: set) -> float:
    """
    Return the similarity score of two shingles
    """
    return len(shingle1 & shingle2) / len(shingle1 | shingle2)

def compareDocs(doc1: str, doc2: str, k: int) -> float:
    """
    Return the similarity score of two documents
    """
    shingles1 = shingles(parseText(doc1), k)
    shingles2 = shingles(parseText(doc2), k)

    return similarityScore(shingles1, shingles2)

def tests():
    shingleSize = 5

    # words = parseText('testdocs/original1.txt')
    # test1 = parseText('testdocs/t1.txt')
    # test2 = parseText('testdocs/t2.txt')
    # test3 = parseText('testdocs/t3.txt')
    # test4 = parseText('testdocs/t4.txt')
    # test5 = parseText('testdocs/t5.txt')

    words = parseText('testdocs/original2.txt')
    test1 = parseText('testdocs/s1.txt')
    test2 = parseText('testdocs/s2.txt')
    test3 = parseText('testdocs/s3.txt')
    test4 = parseText('testdocs/s4.txt')
    test5 = parseText('testdocs/s5.txt')

    shingles1 = shingles(words, shingleSize)
    testShingles1 = shingles(test1, shingleSize)
    testShingles2 = shingles(test2, shingleSize)
    testShingles3 = shingles(test3, shingleSize)
    testShingles4 = shingles(test4, shingleSize)
    testShingles5 = shingles(test5, shingleSize)

    print(similarityScore(shingles1, testShingles1))
    print(similarityScore(shingles1, testShingles2))
    print(similarityScore(shingles1, testShingles3))
    print(similarityScore(shingles1, testShingles4))
    print(similarityScore(shingles1, testShingles5))