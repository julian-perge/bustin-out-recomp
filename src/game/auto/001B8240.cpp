struct S_001B8240
{
    char pad[8];
    unsigned int mask;
    bool FUN_001B8240(int bit) const;
};

// 0x001B8240
bool S_001B8240::FUN_001B8240(int bit) const
{
    return (mask & (1 << bit)) != 0;
}
