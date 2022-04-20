from jaccardsimilarity import parseTextFile, shingles, similarityScore, shinglesString
from pathlib import Path
import time


def test_set_1():
    '''
    Test set 1: test set for first set of documents used to train (manually) the plagiarism detector
    '''
    shingleSize = 5

    testDirPath = Path(__file__).parent.parent / "testdocs"

    # the US Constitution (parts of it)
    words = parseTextFile(Path(testDirPath, "original1.txt"))
    # US Constitution spun and paraphrased
    test1 = parseTextFile(Path(testDirPath, "t1.txt"))
    # US Constitution ran through spinner
    test2 = parseTextFile(Path(testDirPath, "t2.txt"))
    # US Constitution laundered though google translate
    test3 = parseTextFile(Path(testDirPath, "t3.txt"))
    # CCP resolution
    test4 = parseTextFile(Path(testDirPath, "t4.txt"))
    # Articles of Confederation (similar verbage test)
    test5 = parseTextFile(Path(testDirPath, "t5.txt"))

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


def test_set_2():
    '''
    Test set 2: test set for second set of documents used to train (manually) the plagiarism detector
    '''
    shingleSize = 5

    testDirPath = Path(__file__).parent.parent / "testdocs"

    # sample AP English Language and Composition submission, with one testdoc s5 being a submission that has been ran through a spinner
    # https://apcentral.collegeboard.org/pdf/ap20-english-language-and-composition-student-samples-johnson.pdf
    words = parseTextFile(Path(testDirPath, "original2.txt"))
    test1 = parseTextFile(Path(testDirPath, "s1.txt"))
    test2 = parseTextFile(Path(testDirPath, "s2.txt"))
    test3 = parseTextFile(Path(testDirPath, "s3.txt"))
    test4 = parseTextFile(Path(testDirPath, "s4.txt"))
    test5 = parseTextFile(Path(testDirPath, "s5.txt"))

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


def test_set_3():
    '''
    Test set 3: used to see what the backend will be recieving as the parsed text for a submission
    '''
    print(shinglesString(
        "This is a submission for the course \n COP4521 - Secure, \n Parallel and Distributed Computing with Python"))
