## Deep Code Search

In this code base, we demonstrate a joint embedding model based on a code embedding network and description embedding network largely based on work done by https://github.com/guxd/deep-code-search


Our contribution is mostly in ironing out bugs, trying out newer and more complicated models, and setting it up to work with Python.

### Usage
   In order for the codebase to execute, please install requirements as following
   
   ```bash
   pip install -r requirements.txt
   ```

### Train
   
   ```bash
   python codesearcher.py --mode train --language java|python
   ```
   
   ### Code Embedding
   
   ```bash
   python codesearcher.py --mode repr_code --language java|python
   ```
   
   ### Search
   
   ```bash
   python codesearcher.py --mode search --language java|python
   ```