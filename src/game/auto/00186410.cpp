struct S_00186410
{
    struct V
    {
        int d[8];
    };
    int pad;
    V v;
    bool FUN_00186410(const V* s);
};

// 0x00186410
bool S_00186410::FUN_00186410(const V* s)
{
    v = *s;
    return true;
}
