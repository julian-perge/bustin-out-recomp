struct E { char d[0x14]; };
struct S_0010D370 { E* FUN_0010d370(E* p); };
// 0x0010D370
E* S_0010D370::FUN_0010d370(E* p)
{
    E* q = p - 1;
    if (q >= (E*)this)
        return q;
    return (E*)((char*)this + 0x13ec);
}
