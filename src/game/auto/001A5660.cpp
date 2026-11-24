struct S_001A5660
{
    char *p;
    int n;
    S_001A5660 *FUN_001a5660(char *s, int len);
};

// 0x001A5660
S_001A5660 *S_001A5660::FUN_001a5660(char *s, int len)
{
    p = s;
    n = len;
    *s = 0;
    return this;
}
