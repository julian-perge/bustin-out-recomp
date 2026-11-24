struct S_00200870
{
    int a;
    int b;
};

// 0x00200870
void FUN_00200870(S_00200870* dst, const S_00200870* src)
{
    if (dst) {
        dst->a = src->a;
        dst->b = src->b;
    }
}
