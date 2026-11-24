struct S_001B2110
{
    short a;
    int b;
};

// 0x001B2110
void FUN_001B2110(S_001B2110* d, const S_001B2110* s)
{
    if (d) {
        d->a = s->a;
        d->b = s->b;
    }
}
