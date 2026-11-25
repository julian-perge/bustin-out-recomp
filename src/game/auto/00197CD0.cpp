struct S_00197CD0_V
{
    float x;
    float y;
};

struct S_00197CD0
{
    char x;
    char y;
    char z;
    S_00197CD0(const S_00197CD0_V* v);
};

// 0x00197CD0
S_00197CD0::S_00197CD0(const S_00197CD0_V* v)
{
    x = (char)v->x;
    y = (char)v->y;
    z = 1;
}
