struct S_00199A30
{
    char pad[0x5c];
    unsigned lo : 2;
    unsigned f : 2;
    void FUN_00199a30(unsigned v);
};

// 0x00199A30
void S_00199A30::FUN_00199a30(unsigned v)
{
    f = v;
}
