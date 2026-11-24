struct S_001E40C0_Item
{
    char pad[0x70];
    int v;
};

struct S_001E40C0_Owner
{
    char pad[0x14];
    int off;
};

struct S_001E40C0
{
    int FUN_001e40c0();
};

// 0x001E40C0
int S_001E40C0::FUN_001e40c0()
{
    S_001E40C0_Owner* o = *(S_001E40C0_Owner**)((char*)this - 0x5ec);
    return (*(S_001E40C0_Item**)((char*)this + o->off - 0x500))->v;
}
