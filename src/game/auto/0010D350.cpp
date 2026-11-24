struct E_0010d350
{
    char pad[0x14];
};

struct S_0010d350
{
    E_0010d350 e[256];
    E_0010d350* FUN_0010d350(E_0010d350* p);
};

// 0x0010D350
E_0010d350* S_0010d350::FUN_0010d350(E_0010d350* p)
{
    E_0010d350* q = p + 1;
    if (q == e + 256)
        q = e;
    return q;
}
