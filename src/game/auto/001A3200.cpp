struct S_001A3200
{
    char pad[0x164];
    short v[1];
    void FUN_001a3200(int i, short x);
};

// 0x001A3200
void S_001A3200::FUN_001a3200(int i, short x)
{
    v[i] = x;
}
