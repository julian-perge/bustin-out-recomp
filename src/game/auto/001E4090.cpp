struct S_001E4090_Item
{
    char pad[0x6c];
    int v;
};

struct S_001E4090_Owner
{
    char pad[0x14];
    int off;
};

struct S_001E4090
{
    int FUN_001e4090();
};

// 0x001E4090
int S_001E4090::FUN_001e4090()
{
    S_001E4090_Owner* o = *(S_001E4090_Owner**)((char*)this - 0x5ec);
    return (*(S_001E4090_Item**)((char*)this + o->off - 0x500))->v;
}
