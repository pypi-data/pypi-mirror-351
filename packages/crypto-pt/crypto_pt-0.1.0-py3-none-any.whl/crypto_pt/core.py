# -*- coding: utf-8 -*-

import random
from math import gcd

# ... (todo o código das funções: gerar_numero_aleatorio, miller_rabin,
# inverso_modular, gerar_primo, gerar_chaves_grandes,
# criptografar, descriptografar) ...

def gerar_numero_aleatorio(bits):
    """Gera um número aleatório com um número de bits específico."""
    return random.getrandbits(bits) | (1 << bits - 1) | 1

def miller_rabin(n, k=5):
    """Testa se o número n é primo usando o teste de Miller-Rabin."""
    if n in (2, 3): return True
    if n <= 1 or n % 2 == 0: return False
    r, d = 0, n - 1
    while d % 2 == 0: d //= 2; r += 1
    for _ in range(k):
        a = random.randrange(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else: return False
    return True

def inverso_modular(e, phi):
    """Calcula o inverso modular de e mod phi."""
    d_old, d_new = 0, 1
    r_old, r_new = phi, e
    while r_new > 0:
        quotient = r_old // r_new
        d_old, d_new = d_new, d_old - quotient * d_new
        r_old, r_new = r_new, r_old - quotient * r_new
    if r_old != 1: raise ValueError("'e' não possui inverso modular para o phi fornecido.")
    return d_old % phi

def gerar_primo(bits):
    """Gera um número primo com a quantidade de bits especificada."""
    while True:
        candidato = gerar_numero_aleatorio(bits)
        if miller_rabin(candidato): return candidato

def gerar_chaves_grandes(bits=512):
    """Gera um par de chaves RSA (pública e privada)."""
    p = gerar_primo(bits)
    q = gerar_primo(bits)
    while q == p: q = gerar_primo(bits)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    if gcd(e, phi) != 1: raise ValueError("'e' e 'phi' não são primos entre si.")
    d = inverso_modular(e, phi)
    return ((e, n), (d, n))

def criptografar(mensagem: str, chave_publica: tuple):
    """Criptografa uma mensagem string usando a chave pública RSA."""
    e, n = chave_publica
    mensagem_bytes = mensagem.encode('utf-8')
    mensagem_numerica = int.from_bytes(mensagem_bytes, byteorder='big')
    if mensagem_numerica >= n:
        raise ValueError(
            f"Mensagem muito longa (numericamente) para essa chave pública (tamanho {mensagem_numerica.bit_length()} bits, módulo n {n.bit_length()} bits)."
        )
    return pow(mensagem_numerica, e, n)

def descriptografar(mensagem_criptografada: int, chave_privada: tuple):
    """Descriptografa uma mensagem usando a chave privada RSA."""
    d, n = chave_privada
    mensagem_numerica = pow(mensagem_criptografada, d, n)
    num_bytes = (mensagem_numerica.bit_length() + 7) // 8
    mensagem_bytes = mensagem_numerica.to_bytes(num_bytes, byteorder='big')
    try:
        return mensagem_bytes.decode('utf-8')
    except UnicodeDecodeError:
        raise ValueError("Erro ao decodificar a mensagem. Verifique a chave ou os dados.")
