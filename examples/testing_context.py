import tenseal as ts

poly_modulus_degree = 2 ** 13
plain_modulus = 536903681

# private_context = ts.context( ts.SCHEME_TYPE.BFV, poly_modulus_degree=poly_modulus_degree, plain_modulus=plain_modulus )
private_context = ts.context(ts.SCHEME_TYPE.BFV, poly_modulus_degree=4096, plain_modulus=1032193)
sk = private_context.secret_key()
print( sk )
# print( ts.context_from( private_context.serialize() ) )

# public_context = ts.context_from( private_context.serialize() )
# print( public_context )

# public_context.make_context_public()
# print( public_context )

# serialize_public_context = public_context.serialize()
# print( serialize_public_context )
