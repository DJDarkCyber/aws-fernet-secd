import logging
import boto3
from botocore.exceptions import ClientError
import os
from cryptography.fernet import Fernet
import base64, hashlib

BUCKET = "backups-531"

class awsEncryptedManager:
    def __init__(self):
        pass

    def key_encoder(self, password):
        my_password = password.encode()
        key = hashlib.md5(my_password).hexdigest()
        key_64 = base64.urlsafe_b64encode(key.encode("utf-8"))
        return key_64


    def encrypt_file(self, password, filename):
        key = self.key_encoder(password)
        f = Fernet(key)
        output_file = "/tmp/" + filename.split("/")[-1]
        with open(filename, 'rb') as file:
            file_data = file.read()
        
        encrypted_data = f.encrypt(file_data)
        with open(output_file, 'wb') as file:
            file.write(encrypted_data)

        return output_file

    def decrypt_file(self, password, filename):
        key = self.key_encoder(password)
        f = Fernet(key)
        output_file = os.path.expanduser('~/Downloads/') + filename.split("/")[-1]
        with open(filename, 'rb') as file:
            encrypted_data = file.read()
        
        decrypted_data = f.decrypt(encrypted_data)
        with open(output_file, 'wb') as file:
            file.write(decrypted_data)
    
    def upload_file(self, file_name, bucket, password, object_name=None):
        file_name = self.encrypt_file(password, file_name)
        if object_name is None:
            object_name = os.path.basename(file_name)

        s3_client = boto3.client('s3')

        try:
            response = s3_client.upload_file(file_name, bucket, object_name)
        except ClientError as e:
            logging.error(e)
            return False
        os.remove(file_name)
        return True
    
    def download_file(self, file_name, bucket_name, password, object_name=None):
        s3 = boto3.client('s3')
        if object_name is None:
            object_name = file_name

        output_file = "/tmp/" + file_name
        with open(output_file, 'wb') as f:
            s3.download_fileobj(bucket_name, object_name, f)

        self.decrypt_file(password, output_file)
        os.remove(output_file)

    def main(self):
        print("1. Upload file")
        print("2. Download file")
        choice = input("Enter your choice: ")
        if choice == '1':
            file_name = input("File > ")
            object_name = input("Object > ")
            password = input("Password > ")
            if object_name == '':
                object_name = None
            self.upload_file(file_name, BUCKET, password, object_name)
        elif choice == '2':
            file_name = input("File > ")
            object_name = input("Object name (optional)> ")
            password = input("Password > ")
            if object_name == '':
                object_name = None
            self.download_file(file_name, BUCKET, password, object_name)

aem = awsEncryptedManager()

while True:
    aem.main()