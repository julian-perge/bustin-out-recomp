struct S_00018670_V
{
    int a;
    float b;
};

struct S_00018670
{
    char pad[0x48];
    int a;
    float b;
    void FUN_00018670(S_00018670_V* out);
};

// 0x00018670
void S_00018670::FUN_00018670(S_00018670_V* out)
{
    float t = b;
    out->a = a;
    out->b = t;
}
