#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "decrypt.h"

#define  TENCENT_KEY  (char *)"4c5cf7a8f3b4ab22"

int TeDecode(const char* src_code) {
  //printf("src_code:%s\n", src_code);
  char desc[1024*4] = {0};
  int desc_size = sizeof(desc);

  char encrypt_src[1024*32]={0};
  int encrypt_size = sizeof(encrypt_src);

  int iRet = base64_decode(src_code, strlen(src_code), encrypt_src, encrypt_size);
  if(iRet != 0)
  {
    printf("tedecode.so debase64 failed\r\n");
    return -1;
  }

  /*
  printf("hex data: ");
  for(int i = 0; i < encrypt_size; i++) {
    printf("%02x",(unsigned char)encrypt_src[i]);
  }
  printf("\r\n");
  */

  if (DecryptData((BYTE *)encrypt_src, (const int)encrypt_size, (BYTE *)TENCENT_KEY, (BYTE *)desc, &desc_size)) {
    //printf("decrypt string is %s\r\n", desc);
  }
  return atoi(desc);
}

int main(){
    int ret = TeDecode("0WOBjxl7aetn9kikGYbrCDYd0/S9YvqI");
    printf("Res:%d\n", ret);
    return 0;
}
