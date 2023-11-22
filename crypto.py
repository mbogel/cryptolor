#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

#sudo apt install python3-cryptography
#if version too old
#sudo apt install python3-pip
#pip install --no-cache-dir --upgrade cryptography

class Crypto:
    
    def __init__(self):
        pass

    def gen_salt(self):
        salt = os.urandom(16)
        return base64.urlsafe_b64encode(salt)

    def gen_key(self, password, salt):
        salt = base64.urlsafe_b64decode(salt)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key

    def decrypt(self, key, cypher_bytes):
        f = Fernet(key)
        clear_bytes = f.decrypt(cypher_bytes)
        return clear_bytes

    def encrypt(self, key, clear_bytes):
        f = Fernet(key)
        cypher_bytes = f.encrypt(clear_bytes)
        return cypher_bytes