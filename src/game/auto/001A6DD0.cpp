struct S_001A6DD0
{
    char pad[0x10];
    int v;
    bool FUN_001a6dd0(int* out);
};

// 0x001A6DD0
bool S_001A6DD0::FUN_001a6dd0(int* out)
{
    if (v != -1)
    {
        *out = v;
        return true;
    }
    return false;
}
