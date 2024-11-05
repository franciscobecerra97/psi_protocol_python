import random
from oprf import client_prf_offline, server_prf_online_parallel, order_of_generator, G
from parameters import sigma_max, hash_seeds, plain_modulus, output_bits, number_of_hashes, poly_modulus_degree
from simple_hash import Simple_hash
from cuckoo_hash import reconstruct_item, Cuckoo
import numpy as np
from math import log2
from auxiliary_functions import power_reconstruct, windowing
from fastecdsa.curve import P192
from fastecdsa.point import Point
import tenseal as ts
import hashlib
import time
from random import sample

ell = 1
alpha = 3
bin_capacity = 6

minibin_capacity = int( bin_capacity / alpha )
number_of_bins = 2 ** output_bits

base = 2 ** ell
logB_ell = int( log2( minibin_capacity ) / ell ) + 1

def import_data( path = "", elliptical_curve_encryption_secret_key = None, print_label = "ALL" ):	
    
    dataset = []
    f = open( path, 'r' )
    lines = f.readlines()
    for item in lines:
        value = item.replace('\n', '')
        hash_value = int(hashlib.md5(value.encode()).hexdigest(), 16)
        # hash_value = hex( value )
        dataset.append( hash_value )

        if( print_label == "ALL" ): print(  hex(hash_value) + " - " + str( value ), end="\n" )
        if( print_label == "ID" ): print( hash_value, end="\n" )
        if( print_label == "NAME" ): print( value, end="\n" )

    f.close()
    
    if( elliptical_curve_encryption_secret_key is not None ):
        oprf_key = elliptical_curve_encryption_secret_key 
        point_precomputed = ( oprf_key % order_of_generator ) * G 

        dataset = [ client_prf_offline( item, point_precomputed ) for item in dataset ]
    
    return dataset

def elliptical_curve_to_sigma_bits( dataset ):
    
    curve_used = P192
    prime_of_curve_equation = curve_used.p
    
    log_p = int( log2( prime_of_curve_equation ) ) + 1
    prime_of_curve_equation = curve_used.p
    mask = 2 ** sigma_max - 1
    
    vector_of_points = [ Point(pair[0],pair[1], curve=curve_used) for pair in dataset ]
    
    return [ ( Q.x >> log_p - sigma_max - 10 ) & mask for Q in vector_of_points ]

def encrypt( dataset = [], secret_key = 0 ):	

    PRFed_dataset = server_prf_online_parallel( secret_key, dataset )    
    return PRFed_dataset

def simple_hasing( dataset = []):

    SH = Simple_hash( hash_seed = hash_seeds )
    for item in dataset:
        for i in range(number_of_hashes):
            SH.insert(item, i)
    
    dummy_value = random.randint(0,2**63)
    # log_no_hashes = int( log2( number_of_hashes ) ) + 1
    # dummy_value = 2 ** ( sigma_max - output_bits + log_no_hashes ) + 1 

    # simple_hashed_data is padded with dummy_msg_serve
    number_of_bins = 2 ** output_bits
    for i in range(number_of_bins):
        for j in range(bin_capacity):
            if SH.simple_hashed_data[i][j] == None:
                SH.simple_hashed_data[i][j] = dummy_value
    
    return SH.simple_hashed_data 

def particion_and_polynomial( dataset = [] ):
    
    poly_coeffs = []
    for i in range( number_of_bins ):
        coeffs_from_bin = []
        for j in range( alpha ):
            # 1: PARTITIONING
            roots = [ dataset[ i ][ minibin_capacity * j + r ] for r in range( minibin_capacity ) ]
            # 2: FINDING THE POLYNOMIALS IN EACH PARTITION
            coeffs_from_bin = coeffs_from_bin + coeffs_from_roots( roots, plain_modulus ).tolist()
        poly_coeffs.append( coeffs_from_bin )

    return poly_coeffs

def cuckoo_hashing( dataset = [] ):
    
    CH = Cuckoo( hash_seeds )
    for item in dataset:
        CH.insert( item )

    dummy_value = random.randint(0,2**63)
    # log_no_hashes = int( log2( number_of_hashes ) ) + 1
    # dummy_value = 2 ** ( sigma_max - output_bits + log_no_hashes ) + 1 

    # We padd the Cuckoo vector with dummy messages
    for i in range( CH.number_of_bins ):
        if ( CH.data_structure[ i ] == None ):
            CH.data_structure[ i ] = dummy_value

    return CH.data_structure

def windowing_process( dataset = [] ):
    
    windowed_items = []
    for item in dataset:
        windowed_items.append( windowing( item, minibin_capacity, plain_modulus ))
    
    return windowed_items

def batching_process( dataset = [], private_context = None ): # data is 2 x 32
    
    plain_query = [ None for k in range( len( dataset ) ) ] # 1 x 32
    enc_query = [[ None for j in range( logB_ell )] for i in range( 1, base ) ] # 2 x 1

    for j in range( logB_ell ):
        for i in range( base-1 ):
            if ( (i + 1) * base ** j - 1 < minibin_capacity ):
                for k in range( len( dataset ) ):
                    plain_query[ k ] = dataset[ k ][ i ][ j ]                
                enc_query[ i ][ j ] = ts.bfv_vector( private_context, plain_query )
    
    # return { y,  y^2, y^3 ... y^logB_ell }
    return enc_query

def poly_eval( polynomial = [], bathing = [] ):
    '''
    :polynomial: Server polinomial from simple hashing process X
    :bathing: Clinet: batching values from windows and batching Y
    '''

    received_enc_query = bathing # recerving y = [ y, y^2 ]
    all_powers = [None for i in range( minibin_capacity )]

    for i in range(base - 1):
        for j in range( logB_ell ):
            if ((i + 1) * base ** j - 1 < minibin_capacity):
                all_powers[ (i + 1) * base ** j - 1] = received_enc_query[i][j]
    # print( all_powers ) # remove 1d [[ y, y^2 ]] -> [ y, y^2 ]

    for k in range( minibin_capacity ):
        if all_powers[k] == None:
            all_powers[k] = power_reconstruct( received_enc_query, k + 1 )
    all_powers = all_powers[::-1] 
    # print( all_powers ) # inverted the orden or the array [ y, y^2 ] -> [ y^2, y ]

    transposed_poly_coeffs = np.transpose( polynomial ).tolist()
    answer = []

    for i in range( alpha ): # 3
        
        dot_product = all_powers[0]
        for j in range( 1, minibin_capacity ):
            
            # y^2 + ( xn * y ) 
            dot_product = dot_product + transposed_poly_coeffs[ ( minibin_capacity + 1 ) * i + j ] * all_powers[ j ]
            print( dot_product )
        
        # y^2 + ( xn * y ) + an
        dot_product = dot_product + transposed_poly_coeffs[ ( minibin_capacity + 1 ) * i + minibin_capacity ]
        answer.append( dot_product )

    # answer = srv_answer = [
        # y^2 + ( x0 * y ) + a0
        # y^2 + ( x1 * y ) + a1
        # y^2 + ( x2 * y ) + a2 
    # ]
    return answer

def find_intersection( ciphertexts, dataset ):

    decryptions = []
    for ct in ciphertexts:
        decryptions.append( ct.decrypt() )

    # count = [0] * alpha
    # client_intersection = []
    for j in range( alpha ):
        for i in range( 2 ** output_bits ):
            if decryptions[j][i] == 0:
                print( "Element in commun in the position: " + str( [j] ), str( [i] ) )
                # count[j] = count[j] + 1
                # Here we recover this element from the Cuckoo hash structure
    #             PRFed_common_element = reconstruct_item(recover_CH_structure[i], i, hash_seeds[recover_CH_structure[i] % (2 ** log_no_hashes)])
    #             index = PRFed_client_set.index(PRFed_common_element)
    #             client_intersection.append(int(client_set_entries[index][:-1]))

def coeffs_from_roots(roots, modulus):
    '''
    :param roots: an array of integers
    :param modulus: an integer
    :return: coefficients of a polynomial whose roots are roots modulo modulus
    '''
    coefficients = np.array( 1, dtype = np.int64 )
    for r in roots:
        coefficients = np.convolve( coefficients, [1, -r] )
    return coefficients

if __name__ == '__main__':

#  Data generation
# ##############################

    server_size = 1000
    client_size = int( server_size / 1 )
    intersection_size = int( client_size / 2 )

    disjoint_union = sample(range(2 ** 12), server_size + client_size)
    intersection = disjoint_union[:intersection_size]
    server_set = intersection + disjoint_union[intersection_size: server_size]
    client_set = intersection + disjoint_union[server_size: server_size - intersection_size + client_size]

    # evaluation_mode = 'single'
    evaluation_mode = 'multiple'

#  Client
# ##############################
    
    # original data    
    # Y = [ 100 ]
    # Y = [ 100, 150, 300, 800 ]
    Y = client_set

    # vectorizing
    context = ts.context( ts.SCHEME_TYPE.BFV, poly_modulus_degree=poly_modulus_degree, plain_modulus=plain_modulus )
    
    if( evaluation_mode == 'single' ):
        Y_vector = [ ts.bfv_vector( context, [ i ] ) for i in Y ]

    if( evaluation_mode == 'multiple' ):
        Y_vector = ts.bfv_vector( context, Y )
    # print( Y_vector )

#  Server
# ##############################

    # original data
    # X = [ 100 ]
    # X = [ 300 ]
    # X = [ 100, 250, 300, 500 ] 
    X = server_set

    # Polynomial evaluation
    start = time.time()

    if( evaluation_mode == 'single' ):
        evaluations = []
        for y in Y_vector:
            r = random.randint( 0, 2 ** 63 )
            eval = 1
            for x in X:
                # r * ( y - x )
                eval = eval * ( y - [ x ] )
            evaluations.append( eval )
    
    if( evaluation_mode == 'multiple' ):
        r = random.randint( 0, 2 ** 63 )
        evaluations = r * ( Y_vector - X )
    
    # print( evaluations )

# #  Client
# ##############################

    # Solving Polynimial
    if( evaluation_mode == 'single' ):
        result = []
        for eval in evaluations:
            result.append( eval.decrypt() )
    
    if( evaluation_mode == 'multiple' ):
        result = evaluations.decrypt()

    end = time.time()
    
    # Find interception
    # print()
    # if( evaluation_mode == 'single' ):
    #     con = 0
    #     for i in range( len( result ) ):
    #         if( result[ i ][ 0 ] == 0 ):
    #             con = con + 1
    #             print( str( Y[ i ] ) + " was found it!" )

    #     if( con == 0 ):
    #         print( "No elements were found in common" )

    # if( evaluation_mode == 'multiple' ):

    # print( Y )
    # print( X )

    # print( result )

    print( "\ndatabase size: " + str( len( X ) ) + ", mode: " + str( evaluation_mode ) + ", time: " + str( end - start ) + " seconds" )