struct S_0005AA50
{
    unsigned char v;
    bool FUN_0005aa50(unsigned m);
};

// 0x0005AA50
bool S_0005AA50::FUN_0005aa50(unsigned m)
{
    return (v & m) == m;
}
