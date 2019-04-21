## Code summarization using transfer learning


### How to run?

These notebooks should be run sequentially using the docker containers provided below.

1. The first notebook fetches and creates the dataset.
2. The second notebook vectorizes the code sequence and description sequence and trains 3 seq2seq models:
   * Seq2Seq model from function tokens -> docstring
   * Seq2Seq model from api seq -> docstring
   * Seq2Seq model from method name -> docstring
3. This notebook trains an AWD LSTM model for docstring using FastAI's implementation.
4. This notebooks trains the final joint embedder from code to docstring vectors.
5. In this notebook, we build a search engine that uses the trained networks to output query results.
6. This notebook evaluates the model.

In order to run these sets of notebooks (1 - 6), we would highly suggest using these docker containers:

#### Docker Containers

 - [hamelsmu/ml-gpu](https://hub.docker.com/r/hamelsmu/ml-gpu/): Use this container for any *gpu* bound parts.

 - [hamelsmu/ml-cpu](https://hub.docker.com/r/hamelsmu/ml-cpu/): Use this container for any *cpu* bound parts.