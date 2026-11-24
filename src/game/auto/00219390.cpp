struct S_00219390
{
    char f;
    char pad[0x293];
    int v;
    bool FUN_00219390(int x);
};

// 0x00219390
bool S_00219390::FUN_00219390(int x)
{
    if (f)
        v = x;
    return true;
}
