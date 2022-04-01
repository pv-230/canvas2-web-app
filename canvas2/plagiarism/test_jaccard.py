from jaccardsimilarity import parseTextFile, shingles, similarityScore

def test_set_1():
    shingleSize = 5

    words = parseTextFile('testdocs/original1.txt')
    test1 = parseTextFile('testdocs/t1.txt')
    test2 = parseTextFile('testdocs/t2.txt')
    test3 = parseTextFile('testdocs/t3.txt')
    test4 = parseTextFile('testdocs/t4.txt')
    test5 = parseTextFile('testdocs/t5.txt')

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
    shingleSize = 5

    words = parseTextFile('testdocs/original2.txt')
    test1 = parseTextFile('testdocs/s1.txt')
    test2 = parseTextFile('testdocs/s2.txt')
    test3 = parseTextFile('testdocs/s3.txt')
    test4 = parseTextFile('testdocs/s4.txt')
    test5 = parseTextFile('testdocs/s5.txt')

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