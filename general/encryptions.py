from cryptography.fernet import Fernet

# Generate a key and instantiate a Fernet instance
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

# Load the key from the current directory named `secret.key`
def load_key():
    return open("secret.key", "rb").read()

# Encrypts a message
def encrypt(message: str) -> str:
    key = load_key()
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode())
    return encrypted_message.decode()

# Decrypts an encrypted message
def decrypt(encrypted_message: str) -> str:
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message.encode())
    return decrypted_message.decode()

# Example Usage
if __name__ == "__main__":
    generate_key()  # Run this line only once to generate and save the key

    original_message = "This is a secret message"
    encrypted_msg = encrypt(original_message)
    print(f"Encrypted: {encrypted_msg}")

    decrypted_msg = decrypt(encrypted_msg)
    print(f"Decrypted: {decrypted_msg}")
