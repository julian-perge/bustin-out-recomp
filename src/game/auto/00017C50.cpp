struct S_00017C50_v
{
    int a;
    int b;
    int c;
};

struct S_00017C50
{
    char pad[0x24];
    S_00017C50_v v;
    void FUN_00017C50(const S_00017C50_v* s);
};

// 0x00017C50
void S_00017C50::FUN_00017C50(const S_00017C50_v* s)
{
    v = *s;
}
