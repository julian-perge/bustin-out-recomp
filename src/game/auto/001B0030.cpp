struct S_001B0030
{
    int d[11];
    S_001B0030& FUN_001b0030(const S_001B0030& o);
};

// 0x001B0030
S_001B0030& S_001B0030::FUN_001b0030(const S_001B0030& o)
{
    *this = o;
    return *this;
}
