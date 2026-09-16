# ================================================
# 암호 계산 유틸리티 함수 모음
# ================================================

import numpy as np


def gcd(a, b):
    """최대공약수 구하기"""
    while b:
        a, b = b, a % b
    return a


def mod_inverse(a, m):
    """모듈러 역원 구하기"""
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None


def text_to_numbers(text):
    """알파벳을 숫자로 변환 (A=0, B=1, ..., Z=25)"""
    return [ord(c) - ord('A') for c in text.upper() if c.isalpha()]


def numbers_to_text(numbers):
    """숫자를 알파벳으로 변환"""
    return ''.join([chr(int(n) % 26 + ord('A')) for n in numbers])


# ================================================
# 시저 암호 (1단계용)
# ================================================

def caesar_encrypt(plaintext, shift):
    numbers = text_to_numbers(plaintext)
    encrypted = [(n + shift) % 26 for n in numbers]
    return numbers_to_text(encrypted)


def caesar_decrypt(ciphertext, shift):
    numbers = text_to_numbers(ciphertext)
    decrypted = [(n - shift) % 26 for n in numbers]
    return numbers_to_text(decrypted)


# ================================================
# 아핀 암호 (2단계용)
# ================================================

def affine_encrypt(plaintext, a, b):
    if gcd(a, 26) != 1:
        return None
    numbers = text_to_numbers(plaintext)
    encrypted = [(a * m + b) % 26 for m in numbers]
    return numbers_to_text(encrypted)


def affine_decrypt(ciphertext, a, b):
    a_inv = mod_inverse(a, 26)
    if a_inv is None:
        return None
    numbers = text_to_numbers(ciphertext)
    decrypted = [(a_inv * (c - b)) % 26 for c in numbers]
    return numbers_to_text(decrypted)


VALID_A_VALUES = [1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25]


# ================================================
# 힐 암호 (3단계용)
# ================================================

def det_mod26(matrix):
    det = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    return int(det) % 26


def matrix_mod_inverse(matrix):
    det = det_mod26(matrix)
    det_inv = mod_inverse(det, 26)
    if det_inv is None:
        return None

    a, b = matrix[0][0], matrix[0][1]
    c, d = matrix[1][0], matrix[1][1]

    inv_matrix = np.array([
        [d, -b],
        [-c, a]
    ])
    result = (det_inv * inv_matrix) % 26
    return result.astype(int)


def hill_encrypt(plaintext, key_matrix):
    numbers = text_to_numbers(plaintext)
    if len(numbers) % 2 != 0:
        numbers.append(ord('X') - ord('A'))

    encrypted = []
    for i in range(0, len(numbers), 2):
        pair = np.array([[numbers[i]], [numbers[i + 1]]])
        result = np.dot(key_matrix, pair) % 26
        encrypted.extend(result.flatten().astype(int).tolist())

    return numbers_to_text(encrypted)


def hill_decrypt(ciphertext, key_matrix):
    inv_matrix = matrix_mod_inverse(key_matrix)
    if inv_matrix is None:
        return None

    numbers = text_to_numbers(ciphertext)
    decrypted = []
    for i in range(0, len(numbers), 2):
        pair = np.array([[numbers[i]], [numbers[i + 1]]])
        result = np.dot(inv_matrix, pair) % 26
        decrypted.extend(result.flatten().astype(int).tolist())

    return numbers_to_text(decrypted)
