​
## How to run
Check ```requirements.txt``` before running the files (Python 3.12.1 mandatory). You can generate the datasets of the client and the server by running ```set_gen.py```. Then run ```server_offline.py``` and ```client_offline.py``` to preprocess them. Now go the online phase of the protocol by running ```server_online.py``` and ```client_online.py```. Have fun! :smile: 

## How it works
Our implementation is based on this [paper](https://eprint.iacr.org/2017/299.pdf) and its [follow-up](https://eprint.iacr.org/2018/787.pdf). The protocol uses **homomorphic encryption**, a cryptographic primitive that allows *computations on encrypted data* in such a way that only *the secret key holder has access to the decryption of the result of these computations*. For implementing PSI, we used the [FV] homomorphic encryption scheme from the [TenSEAL](https://github.com/OpenMined/TenSEAL) library. You can also check out a concurrent [SEAL](https://github.com/microsoft/SEAL)-based [C++ implementation](https://github.com/microsoft/APSI) of the protocol that has been recently published by Microsoft.

**Disclaimer:** 
* Our implementation is not meant for production use. Use it at your own risk.
* The original version is available here: https://github.com/bit-ml/Private-Set-Intersection/blob/main/README.md