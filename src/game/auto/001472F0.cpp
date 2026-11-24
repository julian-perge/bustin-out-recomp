struct S_001472F0
{
    unsigned FUN_001472f0(unsigned n, int unused);
};

// 0x001472F0
unsigned S_001472F0::FUN_001472f0(unsigned n, int)
{
    n = (n + 3) & ~3u;
    if (n < 8)
        n = 8;
    return n;
}
