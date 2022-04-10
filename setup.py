from setuptools import find_packages, setup
from setuptools.command.install import install
from setuptools.command.develop import develop


def setup_nltk():
    import nltk
    required = ["stopwords", "brown", "omw-1.4", "wordnet", "punkt"]
    for x in required:
        nltk.download(x)


class _PostInstall(install):
    def run(self):
        install.run(self)
        self.execute(setup_nltk, [],
                     msg="Installing NLTK corpora and tokenizers")


class _PostDevelop(develop):
    def run(self):
        develop.run(self)
        self.execute(setup_nltk, [],
                     msg="Installing NLTK corpora and tokenizers")


setup(
    name='canvas2',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'numpy',
        'nltk',
    ],
    cmdclass={'install': _PostInstall, 'develop': _PostDevelop},
)
