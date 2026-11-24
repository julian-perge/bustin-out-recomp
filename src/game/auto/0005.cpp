
struct S_00054A20
{
    int a;
    bool fn_00054A20(const S_00054A20* o);
};
// 0x00054A20
bool S_00054A20::fn_00054A20(const S_00054A20* o)
{
    return a == o->a;
}

struct S_00050B00
{
    float x;
    float y;
    void fn_00050B00(float v);
};
// 0x00050B00
void S_00050B00::fn_00050B00(float v)
{
    y = v;
    x = v;
}

struct S_00051FD0Inner
{
    int a;
    int b;
};

struct S_00051FD0Arg
{
    char pad[0x14];
    S_00051FD0Inner* q;
};

struct S_00051FD0
{
    bool fn_00051FD0(S_00051FD0Arg* p);
};
// 0x00051FD0
bool S_00051FD0::fn_00051FD0(S_00051FD0Arg* p)
{
    return p->q->b != 0;
}

struct S_00053DB0
{
    int a;
    int b;
    int c;
    int d;
    bool e;
    S_00053DB0* fn_00053DB0();
};
// 0x00053DB0
S_00053DB0* S_00053DB0::fn_00053DB0()
{
    d = 0;
    c = 0;
    e = true;
    b = 0;
    return this;
}
