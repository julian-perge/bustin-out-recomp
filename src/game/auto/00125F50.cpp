struct S_00125F50Elem { int a; int b; };
struct S_00125F50
{
    int pad[2];
    S_00125F50Elem e[4];
    int fn_00125F50(unsigned i);
};
// 0x00125F50
int S_00125F50::fn_00125F50(unsigned i)
{
    int r = -1;
    if (i < 4)
        r = e[i].a;
    return r;
}
