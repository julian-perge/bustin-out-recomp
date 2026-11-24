struct S_001864E0
{
    struct V
    {
        int d[7];
    };
    int pad;
    V v;
    bool FUN_001864e0(const V* s);
};

// 0x001864E0
bool S_001864E0::FUN_001864e0(const V* s)
{
    v = *s;
    return true;
}
