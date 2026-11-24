struct S_001B8220
{
    int pad[2];
    unsigned int m;
    void FUN_001b8220(int n);
};

// 0x001B8220
void S_001B8220::FUN_001b8220(int n)
{
    m &= ~(1u << n);
}
