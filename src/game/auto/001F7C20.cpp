struct S_001F7C20
{
    int a;
    int b;
    int c;
    int d;
};

// 0x001F7C20
void FUN_001f7c20(S_001F7C20* r, short dx, short dy)
{
    r->b += dy;
    r->d += dy;
    r->a += dx;
    r->c += dx;
}
