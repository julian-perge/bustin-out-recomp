struct S_001D9790
{
    int x;
    int y;
    S_001D9790& FUN_001D9790(int k);
};

// 0x001D9790
S_001D9790& S_001D9790::FUN_001D9790(int k)
{
    y *= k;
    x *= k;
    return *this;
}
