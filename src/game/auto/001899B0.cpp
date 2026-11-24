struct S_001899B0_in {
    char pad[8];
    short v;
};
struct S_001899B0 {
    char pad[0x174];
    S_001899B0_in* p;
    void FUN_001899b0(int a, short* out);
};
// 0x001899B0
void S_001899B0::FUN_001899b0(int a, short* out)
{
    *out = p->v;
}
