struct S_001E9600_Dst
{
    int d[8];
};

struct S_001E9600
{
    char pad[0x568];
    S_001E9600_Dst s;
    void FUN_001e9600(S_001E9600_Dst* out);
};

// 0x001E9600
void S_001E9600::FUN_001e9600(S_001E9600_Dst* out)
{
    *out = s;
}
