import hashlib
import tenseal as ts
import random
from testing_oprf import oprf
plain_modulus = 536903681
print_len = 1000
process_number = 1

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
    y_index = 0
    evaluations = []
    for y in y_array:
        x_index = 0
        x_top = len( x_array )
        eval = r
        str_eval = "\ty["+ str( y_index ) +"] \t\t" + str( r ) +" * "
        for x in x_array:
            # r * ( y - x )
            x_index = x_index + 1
            if( x_index == x_top ):
                str_eval = str_eval + "( y[" + str( y_index ) +"] - "+ str( x ) +" )"
            else:
                str_eval = str_eval + "( y[" + str( y_index ) +"] - "+ str( x ) +" ) * "
            eval = eval * ( y - [ x ] )
        evaluations.append( eval )
        print( str_eval )
        y_index = y_index + 1
    return evaluations

def decrypt_list( array, key ):
    result = []
    for i in array: 
        result.append( i.decrypt()[0] )
    return result

# Client side
# # # # # # # # # # # # # # # # # # # # 

print( "CLIENT:" )
print( "------------------------------" )

# Pre-processing client
print( str( process_number ) + ") pre-processing " )

client_data = [
    'Francisco BECERRA 23th Belva Luxembourg',
    'Ali Ward 532th Esch-Sur-Alzette Luxembourg',
    'Beatriz Long 12th Luxembourg Luxembourg'
]
print( "\tclient data \t" + print_array( client_data ) )

y = pre_processing( client_data )
print( "\ty \t\t" + str( y ) )

# Server side
# # # # # # # # # # # # # # # # # # # # 

print( "\nSERVER:" )
print( "------------------------------" )

# Pre-processing server
print( str( process_number ) + ") pre-processing " )
process_number = process_number + 1

server_data = [
    'Francisco BECERRA 23th Belva Luxembourg',
    'Fatima Jackson 48th Belva Luxembourg',
    'Gabriel Lewis 901th Belva Luxembourg',
]

print( "\tserver data \t" + print_array( server_data ) )

x = pre_processing( server_data )
print( "\tx \t\t" + str( x ) )
print()

# OPRF

process_number = process_number + 1

y_oprf, x_oprf = oprf( client_data = y, client_key = 12345678910111213, server_data = x, server_key = 12131415161718192 )

y = y_oprf
x = x_oprf

# Client side
# # # # # # # # # # # # # # # # # # # # 

print( "CLIENT:" )
print( "------------------------------" )

# Encryption
print( str( process_number ) + ") Encryption " )
process_number = process_number + 1

context = ts.context( ts.SCHEME_TYPE.BFV, poly_modulus_degree=2 ** 13, plain_modulus=plain_modulus )
key = context.secret_key()
print( "\tkey\t\t" + str( key ) )

_y = encrypt_list( context, y )
print( "\ty^key \t\t" + print_array( _y, _len=36, end=">, " ) )

# Server side
# # # # # # # # # # # # # # # # # # # # 

print( "\nSERVER:" )
print( "------------------------------" )

# Polynomial computation
print( str( process_number ) + ") Polynomial computation " )
process_number = process_number + 1

r = random.randint( 1, plain_modulus )
print( "\tr \t\t" + str( r ) )

# evaluation = r * ( _y - x )
evaluation = poly_eval( x, _y, r )
# print( "\tpoly eval \t" + print_array( evaluation, end="" ) )

# Client side
# # # # # # # # # # # # # # # # # # # # 

print( "\nCLIENT:" )
print( "------------------------------" )

# Decryption
print( str( process_number ) + ") Decryption" )
process_number = process_number + 1

dec = decrypt_list( evaluation, context )

for i in range( len( dec ) ):
    if( dec[ i ] == 0 ):
        print( "\ty["+ str( i ) +"] \t\t" + str( dec[i] ) )
    else:
        print( "\ty["+ str( i ) +"] \t\t" + str( dec[i] ) )
print() 

# Intersection
print( str( process_number ) + ") Intersection" )
process_number = process_number + 1

for i in range( len( dec ) ):
    if( dec[ i ] == 0 ):
        # print( "\t" + client_data[i])
        print( "\ty["+ str( i ) +"] \t\t" + str( client_data[i] ) )
print()




