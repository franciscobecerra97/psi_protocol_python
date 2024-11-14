import tenseal as ts

# Step 1: Party A creates a TenSEAL context with the BFV scheme
# Setting up encryption parameters
poly_modulus_degree = 8192
plain_modulus = 1032193  # Plaintext modulus must be a prime number for BFV

# Party A creates the context with both public and private keys
context = ts.context(
    ts.SCHEME_TYPE.BFV,
    poly_modulus_degree=poly_modulus_degree,
    plain_modulus=plain_modulus
)
sk = context.secret_key()
context.generate_galois_keys()  # Optional for advanced operations
context.generate_relin_keys()  # Optional for advanced operations

# Party A enables public key sharing and deactivates the private key sharing for security
context.make_context_public()
context.global_scale = 2**40
public_context = context.serialize(save_secret_key=False)

# Step 2: Party A encrypts the value X = 100
X = 50
encrypted_X = ts.bfv_vector(context, [X])

# Step 3: Party A shares the public context with Party B
# In real applications, public_context would be sent to Party B through a secure channel
party_B_context = ts.context_from(public_context)

# Step 4: Party B uses the public context to load the encrypted_X
# Party B has the value Y = 50
Y = 50
encrypted_Y = ts.bfv_vector(party_B_context, [Y])

# Step 5: Party B performs the addition operation (X + Y) and sends back the result to Party A
result = encrypted_X - encrypted_Y
result_serialized = result.serialize()  # Serialize result for sending back

# Step 6: Party A receives the result and deserializes it
result_received = ts.bfv_vector_from(context, result_serialized)

# Step 7: Party A decrypts the result and prints it
decrypted_result = result_received.decrypt( secret_key=sk )
print("The result of X + Y is:", decrypted_result[0])
