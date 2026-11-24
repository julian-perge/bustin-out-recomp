struct S_000A42E0
{
    char pad0[0x9c];
    int items[64];
    char pad1[0x164e - 0x9c - 256];
    char cur;
    int FUN_000a42e0();
};

// 0x000A42E0
int S_000A42E0::FUN_000a42e0()
{
    if (cur == -1)
        return 0;
    return items[cur];
}
