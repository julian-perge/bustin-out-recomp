struct S_00210130
{
    char pad[4];
    int r;
    int w;
    int FUN_00210130(int n) const;
};

// 0x00210130
int S_00210130::FUN_00210130(int n) const
{
    return (w - r + n) % 128;
}
