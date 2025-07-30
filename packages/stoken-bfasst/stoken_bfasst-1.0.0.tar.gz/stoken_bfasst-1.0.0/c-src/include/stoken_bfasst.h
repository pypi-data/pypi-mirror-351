#include <string.h>
#include <inttypes.h>

#ifdef _WIN32
#    ifdef STOKEN_BFASST_EXPORTS
#        define STOKEN_BFASST_API __cdecl __declspec(dllexport)
#    else
#        define STOKEN_BFASST_API __cdecl __declspec(dllimport)
#    endif
#else
#    define STOKEN_BFASST_API
#endif

#define STOKEN_TIME_BLOCK_COUNT 5

struct StokenBruteForceAssist {
  unsigned char seed[16];
  char code_out[16];
  unsigned char time_blocks[16 * STOKEN_TIME_BLOCK_COUNT];
  int digits;
  int key_time_offset;
};

STOKEN_BFASST_API
int
stoken_bfasst_generate_passcode(struct StokenBruteForceAssist *assist);

/* Search seed in an array of 16-byte seeds that results in a particular
 * `code_out` that matches `wanted_code`.
 *
 * The number of 16-byte entries in `seeds` must be equal to `seeds_count`.
 * If found, the index of the seed entry is written to `*found_seed_index_out`.
 */
STOKEN_BFASST_API
int
stoken_bfasst_search_seed(
    struct StokenBruteForceAssist *A,
    char *wanted_code,
    unsigned char *seeds,
    size_t seeds_count,
    size_t *found_seed_index_out
);
