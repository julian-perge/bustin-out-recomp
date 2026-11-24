struct S_00069E40
{
    char pad[0x470];
    float v;
    void fn_00069E40(float x);
};

// 0x00069E40
void S_00069E40::fn_00069E40(float x)
{
    v = x;
}

struct S_0006AF50
{
    unsigned flags;
    float a;
    float b;
    void fn_0006AF50(float x);
    void fn_0006AF70(float x);
};

// 0x0006AF50
void S_0006AF50::fn_0006AF50(float x)
{
    flags |= 1;
    a = x;
}

// 0x0006AF70
void S_0006AF50::fn_0006AF70(float x)
{
    flags |= 2;
    b = x;
}

struct S_0006FE70
{
    char pad[0x40];
    int a;
    int b;
    void fn_0006FE70(int x, int y);
};

// 0x0006FE70
void S_0006FE70::fn_0006FE70(int x, int y)
{
    a = x;
    b = y;
}

struct S_00063CB0
{
    char pad[0x52c];
    int n;
    char pad2[0x564 - 0x530];
    bool b;
    bool fn_00063CB0();
};
// 0x00063CB0
bool S_00063CB0::fn_00063CB0()
{
    if (n > 0)
        return true;
    return b;
}
