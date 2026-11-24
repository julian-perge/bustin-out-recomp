struct S_000DCD20
{
    int a;
    int b;
};

// 0x000DCD20
void FUN_000dcd20(S_000DCD20* dst, S_000DCD20* src)
{
    if (dst) {
        dst->a = src->a;
        dst->b = src->b;
    }
}
