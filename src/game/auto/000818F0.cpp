struct S_000818F0
{
    char pad0[0x84];
    bool changed;
    char pad1;
    char v;
    void FUN_000818f0(char a);
};

// 0x000818F0
void S_000818F0::FUN_000818f0(char a)
{
    bool c = a != v;
    v = a;
    changed = c;
}
