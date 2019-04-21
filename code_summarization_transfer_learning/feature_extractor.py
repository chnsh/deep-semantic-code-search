import ast
import re
from typing import List

import astor
import en_core_web_sm
import pandas as pd
from nltk import RegexpTokenizer
from visitor import ASTVisitor

EN = en_core_web_sm.load()

r1 = re.compile(r"([A-Z]+)([A-Z][a-z])")
r2 = re.compile(r"([a-z\d])([A-Z])")


def underscore(word):
    if not isinstance(word, str):
        return word
    word = r1.sub(r'\1_\2', word)
    word = r2.sub(r'\1_\2', word)
    word = word.replace("-", "_")
    return word.lower()


def tokenize_docstring(text):
    """Apply tokenization using spacy to docstrings."""
    tokens = EN.tokenizer(text)
    return [token.text.lower() for token in tokens if not token.is_space]


def tokenize_code(text):
    """A very basic procedure for tokenizing code strings."""
    return RegexpTokenizer(r'\w+').tokenize(text)


def get_function_docstring_pairs(blob):
    """Extract (function/method, docstring) pairs from a given code blob."""
    pairs = []
    try:
        module = ast.parse(blob)
        classes = [node for node in module.body if isinstance(node, ast.ClassDef)]
        functions: List[ast.FunctionDef] = [node for node in module.body if
                                            isinstance(node, ast.FunctionDef)]
        for _class in classes:
            functions.extend([node for node in _class.body if isinstance(node, ast.FunctionDef)])

        for f in functions:
            visitor = ASTVisitor()
            source = astor.to_source(f)
            docstring = ast.get_docstring(f) if ast.get_docstring(f) else ''
            function = source.replace(ast.get_docstring(f, clean=False),
                                      '') if docstring else source

            visitor.visit(ast.parse(function))
            underscored_function_name = underscore(f.name)
            pairs.append((underscored_function_name,
                          f.lineno,
                          source,
                          ' '.join(tokenize_code(function)),
                          ' '.join(tokenize_docstring(docstring.split('\n\n')[0])),
                          ' '.join(
                              [underscore(str(token)) for token in visitor.api_seq]),
                          ' '.join(token for token in underscored_function_name.split("_") if token)
                          ))
    except (AssertionError, MemoryError, SyntaxError, UnicodeEncodeError, OverflowError):
        pass
    return pairs


def get_function_docstring_pairs_list(blob_list):
    """apply the function `get_function_docstring_pairs` on a list of blobs"""
    return [get_function_docstring_pairs(b) for b in blob_list]


if __name__ == '__main__':
    # df = pd.concat([pd.read_csv(
    #     f'https://storage.googleapis.com/kubeflow-examples/code_search/raw_data/00000000000{i}.csv') \
    #                 for i in range(1)])
    df = pd.read_csv('/Users/chintanshah/Downloads/000000000001.csv')

    df['nwo'] = df['repo_path'].apply(lambda r: r.split()[0])
    df['path'] = df['repo_path'].apply(lambda r: r.split()[1])
    df.drop(columns=['repo_path'], inplace=True)
    df = df[['nwo', 'path', 'content']]

    get_function_docstring_pairs_list(df.content.tolist())
