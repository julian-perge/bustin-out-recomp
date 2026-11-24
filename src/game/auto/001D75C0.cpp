struct S_001D75C0_obj
{
    char pad[0x5c];
    unsigned int flags;
};

struct S_001D75C0
{
    char pad[8];
    S_001D75C0_obj* o;
    bool FUN_001D75C0();
};

// 0x001D75C0
bool S_001D75C0::FUN_001D75C0()
{
    return o && (o->flags & 0xc) == 4;
}
