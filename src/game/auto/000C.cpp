struct S_000C1510
{
    unsigned flags;
    int pad;
    int pad2;
    float v;
    void fn_000C1510(float x);
};

// 0x000C1510
void S_000C1510::fn_000C1510(float x)
{
    flags |= 4;
    v = x;
}
