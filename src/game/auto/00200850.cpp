struct S_00200850
{
    int a;
    int b;
};

// 0x00200850
void FUN_00200850(S_00200850* dst, const S_00200850* src)
{
    if (dst) {
        dst->a = src->a;
        dst->b = src->b;
    }
}
