import numpy as np
from .core import (
    generate_k_vector, generate_K_poly,
    encrypt_message, decrypt_ciphertext,
    multiply_matrix_polynominals, add_ciphertexts, multiply_ciphertexts,
    save_json, load_json, matrix_list_to_numpy, matrix_to_numpy
)
import os

def generate_keys(N, p, lam, omega, delta):
    K_poly = generate_K_poly(N, p, lam, omega)
    k_vec = generate_k_vector(N, p)

    R_poly = [np.random.randint(0, p, size=(N, N)) for _ in range(delta * lam)]
    evk = multiply_matrix_polynominals(R_poly, K_poly, p)

    save_json(K_poly, os.path.join("keys/secret_key.json"))
    save_json(k_vec, os.path.join("keys/secret_vector.json"))
    save_json(evk, os.path.join("keys/evaluation_key.json"))

    return True

def encrypt(secret_key_file, vector_file, message, N, p, lam, psi, output_file):
    K_poly = matrix_list_to_numpy(load_json(secret_key_file))
    k_vec = matrix_to_numpy(load_json(vector_file))

    from .core import generate_M_matrix
    M = generate_M_matrix(K_poly, k_vec, message, p)

    ciphertext = encrypt_message(K_poly, M, N, p, lam, psi)
    save_json(ciphertext, output_file)
    return ciphertext

def decrypt(ciphertext_file, secret_key_file, vector_file, p):
    C_poly = matrix_list_to_numpy(load_json(ciphertext_file))
    K_poly = matrix_list_to_numpy(load_json(secret_key_file))
    k_vec = matrix_to_numpy(load_json(vector_file))

    return decrypt_ciphertext(C_poly, K_poly, k_vec, p)

def operate(ciphertext_file1, ciphertext_file2, operation, p, output_file, evaluation_key_file=None):
    C1 = matrix_list_to_numpy(load_json(ciphertext_file1))
    C2 = matrix_list_to_numpy(load_json(ciphertext_file2))

    if operation == "add":
        result = add_ciphertexts(C1, C2, p)
    elif operation == "mul":
        if evaluation_key_file is None:
            raise ValueError("Для операции умножения требуется файл ключа вычислений.")
        evk = matrix_list_to_numpy(load_json(evaluation_key_file))
        result = multiply_ciphertexts(C1, C2, evk, p)
    else:
        raise ValueError("Неподдерживаемая операция. Используй 'add' или 'mul'.")

    save_json(result, output_file)
    return result

