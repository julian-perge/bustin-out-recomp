// 0x00011970
unsigned char __stdcall FUN_00011970(unsigned char* p)
{
    if (++*p >= 6)
        *p = 0;
    return *p;
}
