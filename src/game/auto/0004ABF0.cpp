// 0x0004ABF0
int FUN_0004abf0(int x)
{
    int n = 0;
    while (x != 1) {
        x >>= 1;
        n++;
    }
    return n;
}
