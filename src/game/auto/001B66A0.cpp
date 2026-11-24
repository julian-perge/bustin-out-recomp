struct S_001B66A0
{
    void FUN_001b66a0(int* out);
};

// 0x001B66A0
void S_001B66A0::FUN_001b66a0(int* out)
{
    const int* p = (const int*)this;
    out[0] = p[-33];
    out[1] = p[-32];
}
