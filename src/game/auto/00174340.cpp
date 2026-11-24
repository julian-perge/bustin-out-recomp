// 0x00174340
int FUN_00174340(int a, int b)
{
    int r = b >> a;
    if (r <= 0)
        r = 1;
    return r;
}
