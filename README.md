This repository contains a simplified version of the original implementation published at [https://github.com/bit-ml/Private-Set-Intersection/tree/main](https://github.com/bit-ml/Private-Set-Intersection/tree/main). In this version, you'll find an additional folder called `examples`, which includes various examples that demonstrate the final version of the protocol in an easy-to-understand way. The purpose of this repository is to provide a basic, academic-focused version of the original implementation.
​
### How to Run the Original Version

1. **Set Up the Environment**  
- Review the `requirements.txt` file for a list of necessary Python libraries.
- We recommend using Python version 3.12.1 and a Linux environment for best compatibility.
- For setup guidance, check out this [Codespace tutorial](https://www.youtube.com/watch?v=_01iCF9sO1c&ab_channel=GitHub).

2. **Run the Process**  
- **Step 1:** Run `python set_gen.py` to generate the server and client testing databases.
- **Step 2:** Execute `python server_offline.py` and `python client_offline.py` to preprocess the data as part of the offline phase.
- **Step 3:** In one terminal, start the server with `python server_online.py`. (This process will wait for the client to complete.)
- **Step 4:** In a separate terminal, run `python client_online.py` to complete the process.

## Addicional files


### How It Works

This project is based on the [original repository](https://github.com/bit-ml/Private-Set-Intersection), which provides a Python implementation of the protocols discussed in two papers: [2017/299](https://eprint.iacr.org/2017/299.pdf) and [2018/787](https://eprint.iacr.org/2018/787.pdf).

The protocol uses homomorphic encryption, a cryptographic method that allows computations on encrypted data such that only the holder of the secret key can decrypt the result. Specifically, this project implements Private Set Intersection (PSI) using the FV homomorphic encryption scheme provided by the TenSEAL library. 

For further details, you may also refer to a recent SEAL-based C++ implementation of the protocol, published by Microsoft.

Additionally, a simplified explanation of the code and paper is available on the [Bit-ML GitHub blog](https://bit-ml.github.io/blog/post/private-set-intersection-an-implementation-in-python/).

**Disclaimer:** 
* This implementation is not for production use.
* The original version is available here: https://github.com/bit-ml/Private-Set-Intersection/tree/main