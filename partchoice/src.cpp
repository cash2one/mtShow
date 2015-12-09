#include <openssl/md5.h>
#include <zlib.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int GtAdpLogsMd5(char* pszBuffer, int iPart);

int GtAdpLogsMd5(char* pszBuffer, int iPart)
{
    MD5_CTX stMd5;
    int iCount = 0;
    char szMd1[32] = { 0 };
    char szMd2[32] = { 0 };
    unsigned char  uszMd5[16] = { 0 };

    MD5_Init(&stMd5);
    MD5_Update(&stMd5, pszBuffer, strlen(pszBuffer));
    MD5_Final(uszMd5, &stMd5);

    for (; iCount < 8; iCount ++) {
        sprintf(szMd1 + strlen(szMd1), "%02x", uszMd5[iCount]);
    }
    for (; iCount < 16; iCount ++) {
        sprintf(szMd2 + strlen(szMd2), "%02x", uszMd5[iCount]);
    }

    return (strtoull(szMd1, NULL, 16) + strtoull(szMd2, NULL, 16)) % iPart;
}

int main(int argc, char **argv)
{
    char buf[128] = "0a67f517000054253dc33c1c0020267a+1";
    int partition = 12;

    GtAdpLogsMd5(buf, partition);

    return 0;
}
