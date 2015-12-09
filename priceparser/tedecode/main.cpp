#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "decrypt.h"

int main(int argc, char ** argv) {
  char desc[1024*4] = {0};
  int desc_size = sizeof(desc);
  if (argc <= 2) {
    printf("Usage: decrypt encrypt_key encrypt_string\r\n");
    return -1;
  }

  printf("key is %s\r\n",argv[1]);
  printf("encrypt string is %s\r\n", argv[2]);

  char encrypt_src[1024*32]={0};
  int encrypt_size = sizeof(encrypt_src);

  int iRet = base64_decode(argv[2], strlen(argv[2]), encrypt_src, encrypt_size);
  if(iRet != 0)
  {
    printf("debase64 failed\r\n");
    return -1;
  }

  printf("hex data: ");
  for(int i = 0; i < encrypt_size; i++) {
    printf("%02x",(unsigned char)encrypt_src[i]);
  }
  printf("\r\n");

  if (DecryptData((BYTE *)encrypt_src, (const int)encrypt_size, (BYTE *)argv[1], (BYTE *)desc, &desc_size)) {
    printf("decrypt string is %s\r\n", desc);
  }
  return 0;
}
