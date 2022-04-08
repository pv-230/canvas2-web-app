from similarsubstrings import *


def test_set_1():
    '''
    Test set 1: test set for related sentence detection
    '''
    sentences1 = parseTextFile('../testdocs/original1.txt')
    sentences2 = parseTextFile('../testdocs/t2.txt')

    test1 = getHash(sentences1)
    test2 = getHash(sentences2)
    sims = getSimilarSentences(test1, test2)

    # print(len(sims))
    for i, j in sims:
        print(" ".join(sentences1[i-1]))
        print(" ".join(sentences2[j-1]))
        print()


def test_set_2():
    '''
    Test set 2: test set for the contigious substring detection
    '''
    sentences1 = parseTextFile('../testdocs/original2.txt')
    sentences2 = parseTextFile('../testdocs/s5.txt')

    test1 = getHash(sentences1)
    test2 = getHash(sentences2)
    sims = getSimilarSentences(test1, test2)

    for i, j in sims:
        print(getLCS(sentences1[i-1], sentences2[j-1]))
        print()
