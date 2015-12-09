/***************************************************************************
 * 
 * Copyright (c) 2014 Baidu.com, Inc. All Rights Reserved
 * $Id$ 
 * 
 **************************************************************************/
/**
 * @file encryption_test.cpp
 * @date 2014/03/11 09:38:52
 * @version $Revision$ 
 * @brief encryption demo 
 *  
 **/

#include <stdio.h>
#include <iostream>
#include <stdint.h>
#include <string.h>
#include <netinet/in.h>
#include <endian.h>
#include <openssl/hmac.h>
#include <openssl/evp.h>
#include <openssl/bio.h>
#include <openssl/buffer.h>
#include <string>
using namespace std;
using std::string;

static const int INITIALIZATION_VECTOR_SIZE = 16;
static const int CIPHER_TEXT_SIZE = 8;
static const int SIGNATURE_SIZE = 4;
static const int ENCRYPTED_VALUE_SIZE =
        INITIALIZATION_VECTOR_SIZE + CIPHER_TEXT_SIZE + SIGNATURE_SIZE;
static const int HASH_OUTPUT_SIZE = 20;

/*
const char encryption_key_v[] = {
0x00,0x7b,0x62,0x88,0x00,0x30,0x2d,0x13,
0x4c,0xf4,0x0b,0xaa,0x00,0x30,0x2d,0x13,
0x4c,0xf4,0x41,0xce,0x00,0x30,0x2d,0x13,
0x4c,0xf4,0x4c,0xc2,0x82,0xd5,0xf7,0x54
};

const char integrity_key_v[] = {
0x00,0x7b,0x62,0x88,0x00,0x30,0x2d,0x13,
0x4c,0xf4,0xac,0xee,0x00,0x30,0x2d,0x13,
0x4c,0xf4,0xb9,0xba,0x00,0x30,0x2d,0x13,
0x4c,0xf4,0xc3,0x1c,0x4c,0xbd,0x36,0x0d
};
*/

const char encryption_key_v[] = {
0xae,0xdf,0xaa,0x26,0xa0,0x46,0xc8,0xd5,
0x25,0x9d,0x35,0x3e,0x51,0xc3,0xb5,0x4e,
0x2b,0x13,0xe7,0x87,0xb7,0x32,0x07,0xd8,
0x68,0xdf,0x86,0x5b,0x23,0x0a,0xc2,0x8a
};
const char integrity_key_v[] = {
0x5e,0x2f,0xa2,0x6f,0x45,0xf6,0xc5,0x22,
0x89,0x09,0xe1,0x6e,0x93,0x05,0x6b,0xfb,
0x31,0x52,0xf4,0x9b,0xac,0xfc,0x7e,0x67,
0xad,0x9c,0xdd,0x79,0xd9,0x4b,0x04,0xdc
};
static const string ENCRYPTION_KEY(encryption_key_v, 32);
static const string INTEGRITY_KEY(integrity_key_v, 32);

// Definition of htonll
inline uint64_t htonll(uint64_t net_int) {
#if defined(__LITTLE_ENDIAN)
    return static_cast<uint64_t>(htonl(static_cast<uint32_t>(net_int >> 32))) |
            (static_cast<uint64_t>(htonl(static_cast<uint32_t>(net_int))) << 32);
#elif defined(__BIG_ENDIAN)
    return net_int;
#else
#error Could not determine endianness.
#endif
}
// Definition of ntohll
inline uint64_t ntohll(uint64_t host_int) {
#if defined(__LITTLE_ENDIAN)
    return static_cast<uint64_t>(ntohl(static_cast<uint32_t>(host_int >> 32))) |
            (static_cast<uint64_t>(ntohl(static_cast<uint32_t>(host_int))) << 32);
#elif defined(__BIG_ENDIAN)
    return host_int;
#else
#error Could not determine endianness.
#endif
}

// The actual decryption method:
// Decrypts the ciphertext using the encryption key and verifies the integrity
// bits with the integrity key. The encrypted format is:
// {initialization_vector (16 bytes)}{ciphertext (8 bytes)}{integrity (4 bytes)}
// The value is encrypted as
// <value xor HMAC(encryption_key, initialization_vector)> so
// decryption calculates HMAC(encryption_key, initialization_vector) and xor's
// with the ciphertext to reverse the encryption. The integrity stage takes 4
// bytes of <HMAC(integrity_key, value||initialization_vector)> where || is
// concatenation.
// If Decrypt returns true, value contains the value encrypted in ciphertext.
// If Decrypt returns false, the value could not be decrypted (the signature
// did not match).
//
bool decrypt_int64(
    const std::string& encrypted_value, const std::string& encryption_key,
    const std::string& integrity_key, int64_t* value)
{
    // Compute plaintext.
    const uint8_t* initialization_vector = (uint8_t*)encrypted_value.data();
    //len(ciphertext_bytes) = 8 bytes
    const uint8_t* ciphertext_bytes =
            initialization_vector + INITIALIZATION_VECTOR_SIZE;
    //signatrue = initialization_vector + INITIALIZATION_VECTOR_SIZE(16) + CIPHER_TEXT_SIZE(8)
    //len(signature) = 4 bytes
     //len(signature) = 4 bytes
    const uint8_t* signature = ciphertext_bytes + CIPHER_TEXT_SIZE;

    uint32_t pad_size = HASH_OUTPUT_SIZE;
    uint8_t price_pad[HASH_OUTPUT_SIZE];

    //get price_pad using openssl/hmac.h
    if (!HMAC(EVP_sha1(), encryption_key.data(), encryption_key.length(),
              initialization_vector, INITIALIZATION_VECTOR_SIZE, price_pad,
              &pad_size)) {
        return false;
    }
    uint8_t plaintext_bytes[CIPHER_TEXT_SIZE];
    for (int32_t i = 0; i < CIPHER_TEXT_SIZE; ++i) {
        plaintext_bytes[i] = price_pad[i] ^ ciphertext_bytes[i];
    }
    //print debug_info
    /*
    printf("\nciphertext_bytes:");
    for(int size=0;size<CIPHER_TEXT_SIZE;size++){
        printf("%02x",ciphertext_bytes[size]);
    }
    printf("\nprice_pad:");
    for(int size=0;size<HASH_OUTPUT_SIZE;size++){
        printf("%02x",price_pad[size]);
    }
    */

    //value = ntohllprice_pad ^ ciphertext_bytes) 
    memcpy(value, plaintext_bytes, CIPHER_TEXT_SIZE);
    *value = ntohll(*value);  // Switch to host byte order.
    //cout << endl << "value:" << *value ;

    // Verify integrity bits.
    uint32_t integrity_hash_size = HASH_OUTPUT_SIZE;
    uint8_t integrity_hash[HASH_OUTPUT_SIZE];
    const int32_t INPUT_MESSAGE_SIZE = CIPHER_TEXT_SIZE + INITIALIZATION_VECTOR_SIZE;
    uint8_t input_message[INPUT_MESSAGE_SIZE];

    memcpy(input_message, plaintext_bytes, CIPHER_TEXT_SIZE);
    memcpy(input_message + CIPHER_TEXT_SIZE,
           initialization_vector,
           INITIALIZATION_VECTOR_SIZE);

    if (!HMAC(EVP_sha1(), integrity_key.data(), integrity_key.length(),
              input_message, INPUT_MESSAGE_SIZE, integrity_hash,
              &integrity_hash_size)) {
        return false;
    }

    //print debug_info
    /*
   printf("\ninput_message:");
    for(int32_t size=0;size<INPUT_MESSAGE_SIZE;size++){
        printf("%02x",input_message[size]);
    }
    printf("\ninitializatio_hash:");
    for(uint32_t size=0;size<integrity_hash_size;size++){
        printf("%02x",integrity_hash[size]);
    }
    printf("\nsignatre:");
    for(int32_t size=0;size<SIGNATURE_SIZE;size++){
        printf("%02x",signature[size]);
    }
    printf("\n");
    */
    return memcmp(integrity_hash, signature, SIGNATURE_SIZE) == 0;
}

// Adapted from http://www.openssl.org/docs/crypto/BIO_f_base64.html
bool base64_decode(const std::string& encoded, string *output)
{
    // Alwarys assume that the length of base64 encoded string
    // is larger than decoded one
    char *temp = static_cast<char*>(malloc(sizeof(char) * encoded.length()));
    if (temp == NULL) {
        return false;
    }
    BIO* b64 = BIO_new(BIO_f_base64());
    BIO_set_flags(b64, BIO_FLAGS_BASE64_NO_NL);
    BIO* bio = BIO_new_mem_buf(const_cast<char*>(encoded.data()),
                               encoded.length());
    bio = BIO_push(b64, bio);
    int32_t out_length = BIO_read(bio, temp, encoded.length());
    BIO_free_all(bio);
    output->assign(temp, out_length);
    free(temp);
    return true;
}


bool web_safe_base64_decode(const std::string& encoded, string * output)
{
    // convert from web safe -> normal base64.
    string normal_encoded = encoded;
    size_t index = string::npos;
    while ((index = normal_encoded.find_first_of('-', index + 1)) != string::npos) {
        normal_encoded[index] = '+';
    }
    index = string::npos;
    while ((index = normal_encoded.find_first_of('_', index + 1)) != string::npos) {
        normal_encoded[index] = '/';
    }
    return base64_decode(normal_encoded, output);
}

//add padding 
std::string add_padding(const std::string& b64_string) {
    if (b64_string.size() % 4 == 3) {
        return b64_string + "=";
    } else if (b64_string.size() % 4 == 2) {
        return b64_string + "==";
    }
    return b64_string;
}

int jxdecode(const std::string& encryption_value)
{
    std::string padded = add_padding(encryption_value);
    std::string decode_value;
    int64_t act_value = 0 ;
    web_safe_base64_decode(padded,&decode_value);
    if (!decrypt_int64(decode_value,ENCRYPTION_KEY,INTEGRITY_KEY,&act_value))
    {
        cout << encryption_value << " " <<"juxiao decryption failed" << endl;
        return 0;
    }
    return act_value;
}

int main(int argc, const char *argv[])
{
    //std::string encryption_value = "Uja0xQADFz97jEpgW5IA8g0f455XNIjPRj8IqA";
    std::string encryption_value = "VH1aOwACs-17jEpgW5IA8lQp-R6zYiCUCkrZCg";
    std::string padded = add_padding(encryption_value);
    std::string decode_value;
    int64_t act_value = 0 ;
    web_safe_base64_decode(padded,&decode_value);
    cout << endl << "base64_decoded string:" << decode_value << endl;
    if (!decrypt_int64(decode_value,ENCRYPTION_KEY,INTEGRITY_KEY,&act_value))
    {
        cout << "decryption failed";
    }
    cout << jxdecode(encryption_value);
}
