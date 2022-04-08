import nltk

def getCorpora():
    corpora = ['stopwords', 'brown', 'omw-1.4', 'wordnet']
    for x in corpora:
        nltk.download(x)

if __name__ == "__main__":
    getCorpora()