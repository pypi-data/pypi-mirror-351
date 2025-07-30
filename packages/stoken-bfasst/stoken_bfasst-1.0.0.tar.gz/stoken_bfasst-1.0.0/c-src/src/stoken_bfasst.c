
#define STOKEN_BFASST_EXPORTS 1

#include "stoken_bfasst.h"

#include <openssl/conf.h>
#include <openssl/evp.h>
#include <openssl/err.h>

#define AES128_BLOCK_SIZE 16

static int
encrypt_aes_128_ecb(EVP_CIPHER_CTX * ctx, unsigned char *plaintext,
                    int plaintext_len, unsigned char *key,
                    unsigned char *ciphertext)
{
    /* Inspired from https://stackoverflow.com/questions/38342326/aes-256-encryption-with-openssl-library-using-ecb-mode-of-operation */
    int len;
    int ciphertext_len;

    /* Init cipher with cryptographic key. */

    if (1 != EVP_EncryptInit_ex(ctx, EVP_aes_128_ecb(), NULL, key, NULL)) {
        ciphertext_len = -2;
        goto error1;
    }

    EVP_CIPHER_CTX_set_padding(ctx, 0);

    /* Encrypt message */
    if (1 !=
        EVP_EncryptUpdate(ctx, ciphertext, &len, plaintext, plaintext_len))
    {
        ciphertext_len = -3;
        goto error1;
    }

    ciphertext_len = len;

    /* Finalize */
    if (1 != EVP_EncryptFinal_ex(ctx, ciphertext + len, &len)) {
        ciphertext_len = -4;
        goto error1;
    }
    ciphertext_len += len;

error1:
    return ciphertext_len;
}


static int
stoken_bfasst_generate_passcode_helper(
    EVP_CIPHER_CTX *ctx,
    struct StokenBruteForceAssist *A
) {
    unsigned char key[AES128_BLOCK_SIZE], key2[AES128_BLOCK_SIZE];
    int i, j;
    int result;
    int digits = A->digits;
    int kt_offset = A->key_time_offset;

    result = -200;
    if (digits <= 0 || digits > 10) {
        goto error0;
    }
    if (kt_offset < 0 || kt_offset >= 4) {
        goto error0;
    }

    result = -101;
    unsigned char *bl = A->time_blocks;
    int N = AES128_BLOCK_SIZE;

    if (encrypt_aes_128_ecb(ctx, bl + N*0, N, A->seed, key) != N) goto error0;
    if (encrypt_aes_128_ecb(ctx, bl + N*1, N, key, key2) != N) goto error0;
    if (encrypt_aes_128_ecb(ctx, bl + N*2, N, key2, key) != N) goto error0;
    if (encrypt_aes_128_ecb(ctx, bl + N*3, N, key, key2) != N) goto error0;
    if (encrypt_aes_128_ecb(ctx, bl + N*4, N, key2, key) != N) goto error0;

    int off = kt_offset * 4;

    uint32_t tokencode =
        (key[off + 0] << 24) |
        (key[off + 1] << 16) |
        (key[off + 2] << 8) |
        (key[off + 3] << 0);

    /* populate code_out backwards, adding PIN digits if available */
    j = digits;
    A->code_out[j--] = 0;
    for (i = 0; j >= 0; j--, i++) {
        uint8_t c = tokencode % 10;
        tokencode /= 10;
        A->code_out[j] = c + '0';
    }

    result = 0;

error0:
    return result;
}


STOKEN_BFASST_API
int
stoken_bfasst_generate_passcode(
    struct StokenBruteForceAssist *A
) {
    EVP_CIPHER_CTX *ctx;
    int result;

    /* Create and initialize the context */
    if (!(ctx = EVP_CIPHER_CTX_new())) {
        result = -100;
        goto error0;
    }

    result = stoken_bfasst_generate_passcode_helper(ctx, A);

    EVP_CIPHER_CTX_free(ctx);

error0:
    return result;
}


STOKEN_BFASST_API
int
stoken_bfasst_search_seed(
    struct StokenBruteForceAssist *A,
    char *wanted_code,
    unsigned char *seeds,
    size_t seeds_count,
    size_t *found_seed_index_out
) {
    EVP_CIPHER_CTX *ctx;
    int result;

    /* Create and initialize the context */
    if (!(ctx = EVP_CIPHER_CTX_new())) {
        result = -100;
        goto error0;
    }

    result = 0;
    size_t i;
    for (i = 0; i < seeds_count; i++) {
        memcpy(A->seed, seeds + i*AES128_BLOCK_SIZE, AES128_BLOCK_SIZE);
        if (stoken_bfasst_generate_passcode_helper(ctx, A) != 0) {
            result = -103;
            goto error1;
        }
        if (memcmp(A->code_out, wanted_code, A->digits) == 0) {
            *found_seed_index_out = i;
            break;
        }
    }

error1:
    EVP_CIPHER_CTX_free(ctx);

error0:
    return result;
}
