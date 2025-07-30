import argparse
import os
from .interface import generate_keys, encrypt, decrypt, operate

def main():
    parser = argparse.ArgumentParser(description="FHEMP: Гомоморфное шифрование на матричных полиномах")
    subparsers = parser.add_subparsers(dest="command")

    # gen-keys
    gen = subparsers.add_parser("generate_keys", help="Генерация ключей")
    gen.add_argument("--N", type=int, required=True)
    gen.add_argument("--p", type=int, required=True)
    gen.add_argument("--lam", type=int, required=True)
    gen.add_argument("--omega", type=int, required=True)
    gen.add_argument("--delta", type=int, required=True)
    gen.add_argument("--dir", type=str, default="keys_FHEMP")

    # encrypt
    enc = subparsers.add_parser("encrypt", help="Шифрование")
    enc.add_argument("--message", type=int, required=True)
    enc.add_argument("--secret-key", type=str, default="keys_FHEMP/secret_key.json")
    enc.add_argument("--vector", type=str, default="keys_FHEMP/secret_vector.json")
    enc.add_argument("--N", type=int, required=True)
    enc.add_argument("--p", type=int, required=True)
    enc.add_argument("--lam", type=int, required=True)
    enc.add_argument("--psi", type=int, default=2)
    enc.add_argument("--out", type=str, required=True)

    # decrypt
    dec = subparsers.add_parser("decrypt", help="Расшифровка")
    dec.add_argument("--input", type=str, required=True)
    dec.add_argument("--secret-key", type=str, default="keys_FHEMP/secret_key.json")
    dec.add_argument("--vector", type=str, default="keys_FHEMP/secret_vector.json")
    dec.add_argument("--p", type=int, required=True)

    # operate
    op = subparsers.add_parser("operate", help="Гомоморфные операции")
    op.add_argument("--op", choices=["add", "mul"], required=True)
    op.add_argument("--in1", required=True)
    op.add_argument("--in2", required=True)
    op.add_argument("--p", type=int, required=True)
    op.add_argument("--evk", type=str, default="keys_FHEMP/evaluation_key.json")
    op.add_argument("--out", required=True)

    args = parser.parse_args()

    if args.command == "gen-keys":
        generate_keys(args.N, args.p, args.lam, args.omega, args.delta, args.dir)

    elif args.command == "encrypt":
        encrypt(
            secret_key_file=args.secret_key,
            vector_file=args.vector,
            message=args.message,
            N=args.N,
            p=args.p,
            lam=args.lam,
            psi=args.psi,
            output_file=args.out
        )

    elif args.command == "decrypt":
        m = decrypt(args.input, args.secret_key, args.vector, args.p)
        print("Расшифрованное сообщение:", m)

    elif args.command == "operate":
        operate(
            ciphertext_file1=args.in1,
            ciphertext_file2=args.in2,
            operation=args.op,
            p=args.p,
            output_file=args.out,
            evaluation_key_file=args.evk if args.op == "mul" else None
        )

    else:
        parser.print_help()
