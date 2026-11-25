// 0x001B0DB0
unsigned int FUN_001b0db0(unsigned int a, unsigned int b)
{
    if (a)
        return ((a - b - 1) & 3) + 1;
    return 0;
}
