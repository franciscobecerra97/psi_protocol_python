import hashlib
import tenseal as ts
import random
from math import log2
from fastecdsa.curve import P192
from fastecdsa.point import Point

from extras.parameters import sigma_max, plain_modulus
from extras.oprf import server_prf_online_parallel, client_prf_offline, order_of_generator, G, client_prf_online_parallel, server_prf_online_single_thread

plain_modulus = 536903681
print_len = 1000

def pre_processing( data, mod = plain_modulus ):
    result = []
    for value in data:
        value = value.replace('\n', '') # removing spaces
        hash_value = int( hashlib.md5( value.encode() ).hexdigest(), 16 ) % plain_modulus # string to integer
        result.append( hash_value )
    return result

def print_array( array, _len = print_len, start = "", end=", " ):
    index = 0
    top = len( array )
    aux = "["
    for i in array:
        index = index + 1
        i = str( i )
        if( index == top ):
            aux = aux + start + i[ 0:_len ] 
        else:
            aux = aux + start + i[ 0:_len ] + end
    return aux + "]"

def encrypt_list( key, array ):
    result = []
    for i in array: 
        result.append( ts.bfv_vector( key, [i] ) )
    return result

def poly_eval( x_array, y_array, r = 1 ):
    evaluations = []
    for y in y_array:
        eval = r
        for x in x_array:
            # r * ( y - x )
            eval = eval * ( y - [ x ] )
        evaluations.append( eval )
    return evaluations

def decrypt_list( array, key ):
    result = []
    for i in array: 
        result.append( i.decrypt() )
    return result

def oprf_encrypt_client( dataset = [], secret_key = 0 ):	
    oprf_key = secret_key 
    point_precomputed = ( oprf_key % order_of_generator ) * G 

    PRFed_dataset = [ client_prf_offline( item, point_precomputed ) for item in dataset ]
    return PRFed_dataset

def oprf_encrypt_server( dataset = [], secret_key = 0 ):	

    PRFed_dataset = server_prf_online_parallel( secret_key, dataset )    
    # PRFed_dataset = server_prf_online_single_thread( secret_key, dataset )    
    return PRFed_dataset

def elliptical_curve_to_sigma_bits( dataset ):
    
    curve_used = P192
    prime_of_curve_equation = curve_used.p
    
    log_p = int( log2( prime_of_curve_equation ) ) + 1
    prime_of_curve_equation = curve_used.p
    mask = 2 ** sigma_max - 1
    
    vector_of_points = [ Point(pair[0],pair[1], curve=curve_used) for pair in dataset ]
    
    return [ ( Q.x >> log_p - sigma_max - 10 ) & mask for Q in vector_of_points ]

def oprf( client_data, client_key, server_data, server_key, print_process = True, print_ecc = False, process_number = 2 ):
    
    y = client_data
    x = server_data

    # OPRF procolo
    # # # # # # # # # # # # # # # # # # # # 

    print( str( process_number ) + ") OPRF" )

    sk = server_key

    # client oprf encryption
    if( print_process ):
        print( "\tclient" )
        print( "\t\t\ty \t\t" + str( y ) )

    ck = client_key
    if( print_process ): print( "\t\t\tclient_key \t" + str( ck ) )

    y_ck = oprf_encrypt_client( y, ck )
    if( print_ecc ): print( "\t\t\ty_ck \t\t" + print_array( y_ck ) )
    
    y_ck_sigma = elliptical_curve_to_sigma_bits( y_ck )
    if( print_process ): print( "\t\t\ty_ck \t\t" + print_array( y_ck_sigma ) )

    # client to server
    if( print_process ): 
        print( "\n\tclient . > . > . > . server" )
        print( "\n\tserver" )

        print( "\t\t\ty_ck \t\t" + print_array( y_ck_sigma ) )

        print( "\t\t\tserver_key \t" + str( sk ) )

    y_ck_sk = oprf_encrypt_server( y_ck, sk )
    y_ck_sk_sigma = elliptical_curve_to_sigma_bits( y_ck_sk )
    if( print_process ): print( "\t\t\ty_ck_sk \t" + print_array( y_ck_sk_sigma ) )

    # server to client
    if( print_process ): 
        print( "\n\tclient . < . < . < . server" )
        print( "\n\tclient" )

        print( "\t\t\ty_ck_sk \t" + print_array( y_ck_sk_sigma ) )

    ck_inv = pow( ck, -1, order_of_generator )
    if( print_process ): print( "\t\t\tclient_key_inv \t" + str( ck_inv ) )

    y_sk = oprf_encrypt_server( y_ck_sk, ck_inv )
    y_sk_sigma = elliptical_curve_to_sigma_bits( y_sk )
    if( print_process ): print( "\t\t\ty_sk \t\t" + print_array( y_sk_sigma ) )

    # server oprf encryption
    if( print_process ): print( "\n\tserver " )

    x = x
    if( print_process ): print( "\t\t\tx \t\t" + str( x ) )

    sk = server_key
    if( print_process ): print( "\t\t\tserver_key \t" + str( sk ) )

    x_sk = oprf_encrypt_client( x, sk )
    x_sk_sigma = elliptical_curve_to_sigma_bits( x_sk )
    if( print_process ): print( "\t\t\tx_sk \t\t" + print_array( x_sk_sigma ) )
    print()
    
    return y_sk_sigma, x_sk_sigma

def start():
    # print( "CLIENT:" )
    # print( "------------------------------" )

    # 1) Pre-processing
    # print( "1) pre-processing " )

    y = [
        'Francisco BECERRA 23th Belva Luxembourg',
        # 'Ali Ward 532th Esch-Sur-Alzette Luxembourg',
        # 'Beatriz Long 12th Luxembourg Luxembourg'
    ]
    # print( "\tclient data \t" + print_array( y, 50 ) )

    y = pre_processing( y )
    # print( "\ty \t\t" + str( y ) )

    # Server side
    # # # # # # # # # # # # # # # # # # # # 

    # print( "\nSERVER:" )
    # print( "------------------------------" )

    # 1) Pre-processing
    # print( "1) pre-processing " )

    x = [
        'Francisco BECERRA 23th Belva Luxembourg',
        # 'Fatima Jackson 48th Luxembourg Luxembourg',
        # 'Gabriel Lewis 901th Luxembourg Luxembourg',
    ]
    # print( "\tserver data \t" + print_array( x, 50 ) )

    x = pre_processing( x )
    # print( "\tx \t\t" + str( x ) )

    # OPRF procolo
    # # # # # # # # # # # # # # # # # # # # 

    print( "OPRF:" )
    print( "------------------------------" )

    sk = 12131415161718192

    # client oprf encryption
    print( "client" )
    print( "\ty \t\t" + str( y ) )

    ck = 12345678910111213
    print( "\tclient_key \t" + str( ck ) )

    y_ck = oprf_encrypt_client( y, ck )
    y_ck_sigma = elliptical_curve_to_sigma_bits( y_ck )
    print( "\ty_ck \t\t" + print_array( y_ck_sigma ) )

    # client to server
    print( "\nclient . > . > . > . server" )
    print( "\nserver" )

    print( "\ty_ck \t\t" + print_array( y_ck_sigma ) )

    print( "\tserver_key \t" + str( sk ) )

    y_ck_sk = oprf_encrypt_server( y_ck, sk )
    y_ck_sk_sigma = elliptical_curve_to_sigma_bits( y_ck_sk )
    print( "\ty_ck_sk \t" + print_array( y_ck_sk_sigma ) )

    # server to client
    print( "\nclient . < . < . < . server" )
    print( "\nclient" )

    print( "\ty_ck_sk \t" + print_array( y_ck_sk_sigma ) )

    ck_inv = pow( ck, -1, order_of_generator )
    print( "\tclient_key_inv \t" + str( ck_inv ) )

    y_sk = oprf_encrypt_server( y_ck_sk, ck_inv )
    y_sk_sigma = elliptical_curve_to_sigma_bits( y_sk )
    print( "\ty_sk \t\t" + print_array( y_sk_sigma ) )

    # server oprf encryption
    print( "\nserver " )

    x = x
    print( "\tx \t\t" + str( x ) )

    sk = 12131415161718192
    print( "\tserver_key \t" + str( sk ) )

    x_sk = oprf_encrypt_client( x, sk )
    x_sk_sigma = elliptical_curve_to_sigma_bits( x_sk )
    print( "\tx_sk \t\t" + print_array( x_sk_sigma ) )

    print()

# start()