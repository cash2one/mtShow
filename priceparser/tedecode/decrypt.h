/*
 * Encrypt.h
 * cyuezhou@tencent.com
 */

typedef char BYTE;
typedef char BOOL;
typedef unsigned long DWORD;
#define TRUE 1
#define FALSE 0

BOOL DecryptData(const BYTE* pInBuf, int nInBufLen, const BYTE* pKey, BYTE* pOutBuf, int * pOutBufLen);
int base64_decode(char const*in, const int in_len, char *out, int& out_len);

/**/

 