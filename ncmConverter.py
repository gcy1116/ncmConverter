import binascii
import struct
import base64
import json
import os
from Crypto.Cipher import AES

def dump(file_path, output_dir):
    core_key = binascii.a2b_hex('687A4852416D736F356B496E62617857')  # b'hzHRAmso5kInbaxW'
    meta_key = binascii.a2b_hex('2331346C6A6B5F215C5D2630553C2728')  # b"#14ljk_!\\]&0U<'("
    
    unpad = lambda s: s[0:-(s[-1] if type(s[-1]) == int else ord(s[-1]))]

    with open(file_path, 'rb') as f:
        header = f.read(8)
        assert binascii.b2a_hex(header) == b'4354454e4644414d'  # 'CTENEFDAM' in hex, indicating a NCM file magic header

        # seek(offset, whence) 
        # offset: number of bytes to move
        # whence = 0: start of file, 1: current position, 2: end of file

        f.seek(2, 1)  # or header = f.read(10) and assert binascii.b2a_hex(header) == b'4354454e4644414d0170' and # f.seek(2, 1)
        key_length = struct.unpack('<I', bytes(f.read(4)))[0]  # b'\x80\x00\x00\x00' to int 128 (AES three key_len: 128, 192, 256 bits)
        key_data = f.read(key_length)
        key_data_array = bytearray(key_data)
        for i in range(len(key_data_array)):
            key_data_array[i] ^= 0x64  # XOR with 0x64 to get the real key data

        key_data = bytes(key_data_array)
        cryptor = AES.new(core_key, AES.MODE_ECB)
        key_data = unpad(cryptor.decrypt(key_data))[17:]
        key_length = len(key_data)  # 128 - 17 - padding
        key_data = bytearray(key_data)

        # RC4-KSA algorithm to generate the s-box
        key_box = bytearray(range(256))
        c = 0
        last_byte = 0
        key_offset = 0
        for i in range(256):
            swap = key_box[i]
            c = (swap + last_byte + key_data[key_offset]) & 0xff
            key_offset += 1
            if key_offset >= key_length:
                key_offset = 0
            
            key_box[i] = key_box[c]
            key_box[c] = swap
            last_byte = c

        meta_length = struct.unpack('<I', bytes(f.read(4)))[0]
        meta_data_array = bytearray(f.read(meta_length))
        for i in range(len(meta_data_array)):
            meta_data_array[i] ^= 0x63  # XOR with 0x63 to get the real meta data
        meta_data = base64.b64decode(bytes(meta_data_array)[22:])
        cryptor = AES.new(meta_key, AES.MODE_ECB)
        meta_data = unpad(cryptor.decrypt(meta_data)).decode('utf-8')[6:]  # json
        meta_data = json.loads(meta_data)

        crc32 = struct.unpack('<I', bytes(f.read(4)))[0]
        f.seek(5, 1)  # just skip the padding

        image_size = struct.unpack('<I', bytes(f.read(4)))[0]
        image_data = f.read(image_size)

        file_name = meta_data['musicName'] + '.' + meta_data['format']
        output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        output_path = os.path.join(output_dir, file_name)
        with open(output_path, 'wb') as output_file:
            chunk = bytearray()
            while True:
                chunk = bytearray(f.read(0x8000))
                chunk_length = len(chunk)
                if not chunk:
                    break
                for i in range(1,chunk_length+1):
                    j = i & 0xff;
                    chunk[i-1] ^= key_box[(key_box[j] + key_box[(key_box[j] + j) & 0xff]) & 0xff]
                output_file.write(chunk)
            # close(output_file)
        # close(f)
