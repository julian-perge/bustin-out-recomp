struct S_001E8F60
{
    int pad[0x120];
    int v[10];
    int FUN_001e8f60(int n);
};

// 0x001E8F60
int S_001E8F60::FUN_001e8f60(int n)
{
    return v[n + 2] + v[n];
}
