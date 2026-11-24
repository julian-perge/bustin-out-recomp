struct S_00035E30_Obj
{
    char pad[0x1c];
    unsigned int flags;
    bool IsSet() const { return (flags >> 2) & 1; }
};

struct S_00035E30
{
    char pad[0xe4];
    S_00035E30_Obj* o;
    bool FUN_00035e30();
};

// 0x00035E30
// parked: source shape
bool S_00035E30::FUN_00035e30()
{
    if (o)
        return o->IsSet();
    return false;
}
