struct S_001B0060
{
    int d[11];
    S_001B0060& FUN_001b0060(const S_001B0060& o);
};

// 0x001B0060
S_001B0060& S_001B0060::FUN_001b0060(const S_001B0060& o)
{
    *this = o;
    return *this;
}
