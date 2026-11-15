struct Child_00134A70
{
    virtual void v0(int a);
    virtual void v1(int a);
    virtual void v2(int a);
};

struct S_00134A70
{
    char pad[0x20];
    Child_00134A70* child;
    void fn_00134A70(int a);
    void fn_00134A90(int a);
};

// 0x00134A70
void S_00134A70::fn_00134A70(int a)
{
    if (child)
        child->v1(a);
}

// 0x00134A90
void S_00134A70::fn_00134A90(int a)
{
    if (child)
        child->v2(a);
}

struct S_00137B90
{
    const char* s;
    int fn_00137B90();
};

// 0x00137B90
int S_00137B90::fn_00137B90()
{
    const char* p = s;
    const char* q = p + 1;
    char c;
    do
    {
        c = *p;
        p++;
    } while (c);
    return p - q;
}
