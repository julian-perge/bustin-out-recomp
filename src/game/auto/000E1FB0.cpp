struct S_000E1FB0_V
{
    virtual ~S_000E1FB0_V();
};

struct S_000E1FB0
{
    char pad[0x14];
    S_000E1FB0_V* p;
    void FUN_000e1fb0();
};

// 0x000E1FB0
void S_000E1FB0::FUN_000e1fb0()
{
    if (p) {
        delete p;
        p = 0;
    }
}
