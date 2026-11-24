struct S_001A59B0
{
    char pad[0x34];
    int v;
    bool FUN_001a59b0(const S_001A59B0* o);
};

// 0x001A59B0
bool S_001A59B0::FUN_001a59b0(const S_001A59B0* o)
{
    return v == o->v;
}
