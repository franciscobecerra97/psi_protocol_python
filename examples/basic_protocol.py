import hashlib
import tenseal as ts
import random
plain_modulus = 536903681
print_len = 38

def pre_processing( data, mod = plain_modulus ):
    result = []
    for value in data:
        value = value.replace('\n', '') # removing spaces
        hash_value = int( hashlib.md5( value.encode() ).hexdigest(), 16 ) % plain_modulus # string to integer
        result.append( hash_value )
    return result

def print_array( array, _len = print_len, start = "", end = "...," ):
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

# 0) Pre-processing
print( "1) pre-processing " )

client_data = [
    'Francisco BECERRA 23th Belva Luxembourg',
    'Ali Ward 532th Esch-Sur-Alzette Luxembourg',
    'Beatriz Long 12th Luxembourg Luxembourg'
]
print( "\tclient data \t" + print_array( client_data, end=", " ) )

y = pre_processing( client_data )
print( "\ty \t\t" + str( y ) )

# 1) Encryption
print( "\n2) Encryption" )

context = ts.context( ts.SCHEME_TYPE.BFV, poly_modulus_degree=2 ** 13, plain_modulus=plain_modulus )
key = context.secret_key()
print( "\tkey\t\t" + str( key ) )

# 2) Encryption
_y = encrypt_list( context, y )
print( "\ty^key \t\t" + print_array( _y, _len=36, end=">, " ) )

# Server side
# # # # # # # # # # # # # # # # # # # # 

print( "\nSERVER:" )
print( "------------------------------" )

# 0) Pre-processing
print( "1) pre-processing " )

server_data = [
    'Francisco BECERRA 23th Belva Luxembourg',
    'Fatima Jackson 48th Belva Luxembourg',
    'Gabriel Lewis 901th Belva Luxembourg',
]

print( "\tserver data \t" + print_array( server_data, end=", " ) )

x = pre_processing( server_data )
print( "\tx \t\t" + str( x ) )

# 3) Polynomial computation
print( "\n3) Polynomial computation" )

r = random.randint( 1, plain_modulus )
print( "\tr \t\t" + str( r ) )

# evaluation = r * ( _y - x )
evaluation = poly_eval( x, _y, r )
# print( "\tpoly eval \t" + print_array( evaluation, end="" ) )

# Client side
# # # # # # # # # # # # # # # # # # # # 

print( "\nCLIENT:" )
print( "------------------------------" )

# 4. Decryption
dec = decrypt_list( evaluation, context )
# print( "4) Decryption \t\t" + str( dec ) )
print( "\n4) Decryption" )
for i in range( len( dec ) ):
    if( dec[ i ] == 0 ):
        print( "\ty["+ str( i ) +"] \t\t" + str( dec[i] ) )
    else:
        print( "\ty["+ str( i ) +"] \t\t" + str( dec[i] ) )

print( "\n5) Intersection" )
for i in range( len( dec ) ):
    if( dec[ i ] == 0 ):
        # print( "\t" + client_data[i])
        print( "\ty["+ str( i ) +"] \t\t" + str( client_data[i] ) )

print()




