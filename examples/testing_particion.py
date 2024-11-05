import random
from oprf import client_prf_offline, server_prf_online_parallel, order_of_generator, G
from parameters import sigma_max, hash_seeds, plain_modulus, output_bits, number_of_hashes, bin_capacity
from simple_hash import Simple_hash
from cuckoo_hash import reconstruct_item, Cuckoo
import numpy as np
from math import log2
from auxiliary_functions import coeffs_from_roots, power_reconstruct, windowing
from fastecdsa.curve import P192
from fastecdsa.point import Point
import tenseal as ts
from random import sample

server_size = 8
client_size = int( server_size / 2 )
intersection_size = int( client_size / 2 )

plain_modulus = 536903681

def simple_hasing( dataset = []):

    SH = Simple_hash( hash_seed = hash_seeds )
    for item in dataset:
        for i in range(number_of_hashes):
            SH.insert(item, i)
    
    return SH.simple_hashed_data 

def cuckoo_hashing( dataset = [] ):
    
    CH = Cuckoo( hash_seeds )
    for item in dataset:
        CH.insert( item )

    return CH.data_structure

#set elements can be integers < order of the generator of the elliptic curve (192 bits integers if P192 is used); 'sample' works only for a maximum of 63 bits integers.
disjoint_union = sample(range(2 ** 32 - 1), server_size + client_size)
intersection = disjoint_union[:intersection_size]
server_set = intersection + disjoint_union[intersection_size: server_size]
client_set = intersection + disjoint_union[server_size: server_size - intersection_size + client_size]

server_sh = simple_hasing( dataset = server_set )
print( "server_set" )
print( server_set )
print( "server_sh" )
print( server_sh )

client_ch = cuckoo_hashing( dataset = client_set )
print( "client_set" )
print( client_set )
print( "client_ch" )
print( client_ch )