​
## How to run
Firstly, please refer to the ```requirements.txt``` file, which lists all the necessary python libraries. Additional suggestions include using Python version 3.12.1 and running the files in a Linux environment. For guidance on this process, we recommend using Codespace (https://www.youtube.com/watch?v=_01iCF9sO1c&ab_channel=GitHub). The final step is to run the process, which is as follows:
1. Execute the command ```python set_gen.py``` to generate the server and client testing databases.
2. Then, run ```python server_offline.py``` and ```python client_offline.py``` to preprocess them.
3. Run ```python server_online.py``` This process will pull the process waiting for the ```client_online.py``` to complete.
4. Finally, in a different terminal, run ```client_online.py```.

## How it works
Our implementation is based on this [paper](https://eprint.iacr.org/2017/299.pdf) and its [follow-up](https://eprint.iacr.org/2018/787.pdf). The protocol uses **homomorphic encryption**, a cryptographic primitive that allows *computations on encrypted data* in such a way that only *the secret key holder has access to the decryption of the result of these computations*. For implementing PSI, we used the [FV] homomorphic encryption scheme from the [TenSEAL](https://github.com/OpenMined/TenSEAL) library. You can also check out a concurrent [SEAL](https://github.com/microsoft/SEAL)-based [C++ implementation](https://github.com/microsoft/APSI) of the protocol that has been recently published by Microsoft.

**Disclaimer:** 
* Our implementation is not meant for production use. Use it at your own risk.
* The original version is available here: https://github.com/bit-ml/Private-Set-Intersection/tree/main