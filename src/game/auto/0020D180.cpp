// 0x0020D180
int FUN_0020d180(unsigned char v, int n)
{
    int x = (v << 4) | v;
    return x >> ((8 - n) >> 1);
}
