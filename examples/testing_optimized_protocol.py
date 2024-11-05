import random
import numpy as np
from math import log2
from fastecdsa.curve import P192
from fastecdsa.point import Point
import tenseal as ts
import hashlib

from extras.oprf import client_prf_offline, server_prf_online_parallel, order_of_generator, G
from extras.parameters import sigma_max, hash_seeds, plain_modulus, output_bits, number_of_hashes, poly_modulus_degree
from extras.simple_hash import Simple_hash
from extras.cuckoo_hash import reconstruct_item, Cuckoo
from extras.auxiliary_functions import coeffs_from_roots, power_reconstruct, windowing

ell = 1
alpha = 3
bin_capacity = 6
module = 8192

minibin_capacity = int( bin_capacity / alpha )
number_of_bins = 2 ** output_bits

base = 2 ** ell
logB_ell = int( log2( minibin_capacity ) / ell ) + 1

def import_full_data( path = "" ):	
    
    dataset = []
    f = open( path, 'r' )
    lines = f.readlines()
    for item in lines:
        dataset.append( item.replace('\n', '') )

    f.close()
    
    return dataset

def import_and_encrypt_to_elliptical_curve( path = "", secret_key = 0, print_label = "ALL" ):	
    
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

    oprf_key = secret_key 
    point_precomputed = ( oprf_key % order_of_generator ) * G 

    PRFed_dataset = [ client_prf_offline( item, point_precomputed ) for item in dataset ]
    
    return PRFed_dataset

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
    
    # dummy_value = random.randint(0,2**63)
    # log_no_hashes = int( log2( number_of_hashes ) ) + 1
    # dummy_value = 2 ** ( sigma_max - output_bits + log_no_hashes ) + 1 

    # simple_hashed_data is padded with dummy_msg_servere
    number_of_bins = 2 ** output_bits
    for i in range( number_of_bins ):
        for j in range( bin_capacity ):
            if SH.simple_hashed_data[i][j] == None:
                SH.simple_hashed_data[i][j] = random.randint(0,2**63) %module
    
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

    # dummy_value = random.randint(0,2**63) 
    # log_no_hashes = int( log2( number_of_hashes ) ) + 1
    # dummy_value = 2 ** ( sigma_max - output_bits + log_no_hashes ) + 1 

    # We padd the Cuckoo vector with dummy messages
    for i in range( CH.number_of_bins ):
        if ( CH.data_structure[ i ] == None ):
            CH.data_structure[ i ] = random.randint(0,2**63) %module

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
    
    # x: polynomial = []
    # y: bathing = []

    received_enc_query = bathing
    all_powers = [None for i in range( minibin_capacity )]

    for i in range(base - 1):
        for j in range( logB_ell ):
            if ((i + 1) * base ** j - 1 < minibin_capacity):
                all_powers[ (i + 1) * base ** j - 1] = received_enc_query[i][j]
    # print( all_powers ) # remove 1d [[ y0, y1 ]] -> [ y0, y1 ]

    for k in range( minibin_capacity ):
        if all_powers[k] == None:
            all_powers[k] = power_reconstruct( received_enc_query, k + 1 )
    all_powers = all_powers[::-1] # inverted the orden or the array [ y0, y1 ] -> [ y1, y0 ]
    # print( all_powers )

    transposed_poly_coeffs = np.transpose( polynomial ).tolist() # [ x^2, x, a ] -> [ x^2 ][ x ][ a ]
    answer = []

    for i in range( alpha ): # 3
        
        dot_product = all_powers[0]
        for j in range( 1, minibin_capacity ):
            
            # dot_product = y^2 + ( xn * y ) 
            dot_product = dot_product + transposed_poly_coeffs[ ( minibin_capacity + 1 ) * i + j ] * all_powers[ j ]
        
        # dot_product + an ( y^2 + ( xn * y ) + an )
        dot_product = dot_product + transposed_poly_coeffs[ ( minibin_capacity + 1 ) * i + minibin_capacity ]
        answer.append( dot_product )

    # answer = srv_answer = [
        # y^2 + ( x0 * y ) + n0
        # y^2 + ( x1 * y ) + n1
        # y^2 + ( x2 * y ) + n2 
    # ]
    return answer

def find_intersection( ciphertexts, structure = [], pre_dataset = [], dataset = [] ):

    decryptions = []
    for ct in ciphertexts:
        decryptions.append( ct.decrypt() )

    log_no_hashes = int(log2( number_of_hashes )) + 1
    
    for j in range( alpha ):
        for i in range( 2 ** output_bits ):
            if decryptions[j][i] == 0:
                print( 'element found it in: [' + str( j ) + '][' + str(i) + ']' )
                # try:
                #     recover_item = reconstruct_item( structure[i], i, hash_seeds[structure[i] % (2 ** log_no_hashes)])
                #     index = pre_dataset.index( recover_item )
                #     print( dataset[ index ] + ' was found it' )
                # except: None

if __name__ == '__main__':

    # ####################################################################################
    # OPRF protocol
    # ####################################################################################
    
    #  Server
    # ##############################

    # # 1: OPRF encoding
    sk = 1234567891011121314151617181920
    server_sk = import_and_encrypt_to_elliptical_curve( path = "data_set/server", secret_key = sk, print_label="NONE" )
    # print( "\n\n" + str( server_sk ) )

    server_sigm = elliptical_curve_to_sigma_bits( server_sk )
    # print( "\n\n" + str( server_sigm ))
    
    # 2: Simple Hasing
    server_pre = [ i%module for i in server_sigm ]
    server_sh = simple_hasing( dataset = server_pre )
    # print( "\n\n" + str( server_sh ) )

    # 3: Particion & Polynomial calculation
    server_poly = particion_and_polynomial( dataset = server_sh )
    # print( "\n\n" + str( server_poly ) )

    # #  Client
    # # ##############################

    # 1: OPRF encoding
    ck = 12345678910111213141516171819222222222222
    client = import_full_data( path = "data_set/client" )
    client_ck = import_and_encrypt_to_elliptical_curve( path = "data_set/client", secret_key = ck, print_label="NONE" )
    # print( "\n\n" + str( client_ck ) )

    client_cksk = encrypt( client_ck, sk )
    # print( "\n\n" + str( client_cksk ) )
    
    key_inverse = pow( ck, -1, order_of_generator )
    client_sk = encrypt( dataset = client_cksk, secret_key = key_inverse )
    # print( "\n\n" + str( client_sk ) )

    client_sig = elliptical_curve_to_sigma_bits( client_sk )
    # print( "\n\n" + str( client_sig ))
    
    # 2: cuckoo hasing
    client_pre = [ i%module for i in client_sig ]
    # print( "\n\n" + str( client_pre ) )

    client_ch = cuckoo_hashing( dataset = client_pre )
    # print( "\n\n" + str( client_ch ) )

    # # 3: Windowing
    client_win = windowing_process( client_ch )
    # print( "\n\n" + str( client_win ) )

    # 4: Batching
    private_context = ts.context( ts.SCHEME_TYPE.BFV, poly_modulus_degree=poly_modulus_degree, plain_modulus=plain_modulus )
    client_bat = batching_process( client_win, private_context )
    # print( "\n\n" + str( client_bat ) )
    
    # # ####################################################################################
    # # Polynomial evaluations
    # # ####################################################################################
    
    #  server
    # ##############################
    server_client_poly_eval = poly_eval( server_poly, client_bat )
    # print( "\n\n" + str( server_client_poly_eval ) )
    
    # ####################################################################################
    # Find the intersection
    # ####################################################################################

    #  Client
    # ##############################
    find_intersection( ciphertexts = server_client_poly_eval, structure = client_ch, pre_dataset = client_pre, dataset = client )