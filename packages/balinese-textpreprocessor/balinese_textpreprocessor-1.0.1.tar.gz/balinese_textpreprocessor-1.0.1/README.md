# Package for Balinese Text Preprocessing

This is the first package to preprocess your Balinese raw texts. This package provides several functions that you can use for prepare and convert your raw text into clean version.

# Installation

`pip install balinese_textpreprocessor`

# Usage

```
from balinese_textpreprocessor import TextPreprocessor
sentence = "I Budi ngalahin **& I Lutunge 12354!!"
preprocessor = TextPreprocessor()
preprocessed_sentence = preprocessor.case_folding(sentence)
preprocessed_sentence = preprocessor.remove_number(preprocessed_sentence)
preprocessed_sentence = preprocessor.remove_punctuation(
    preprocessed_sentence)
preprocessed_sentence = preprocessor.normalize_words(
    preprocessed_sentence)
preprocessed_sentence = preprocessor.lemmatize_text(
    preprocessed_sentence)
print(preprocessed_sentence)
```

# Acknowledgement

Please cite this paper if you think this package is useful:

[1] Arimbawaa, I. G. A. P., & ERa, N. A. S. (2017). Lemmatization in Balinese language. Jurnal Elektronik Ilmu Komputer Udayana p-ISSN, 2301, 5373.

[2] Pradipthaa, I. G. M. H., & ERa, N. A. S. (2020). Building balinese part-of-speech tagger using hidden markov model (HMM). Jurnal Elektronik Ilmu Komputer Udayana p-ISSN, 2301, 5373.
