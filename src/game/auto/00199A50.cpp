struct S_00199A50
{
    char pad[0x5c];
    unsigned int v;
    void FUN_00199a50(short x);
};

// 0x00199A50
void S_00199A50::FUN_00199a50(short x)
{
    v = (v & 0xffff) | (x << 16);
}
