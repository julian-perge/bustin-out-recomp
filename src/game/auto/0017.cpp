struct S_001753B0
{
    int pad;
    int a;
    int b;
    void fn_001753B0(int x, int y);
};

// 0x001753B0
void S_001753B0::fn_001753B0(int x, int y)
{
    a = x;
    b = y;
}

struct S_00175800
{
    int pad;
    int a;
    int b;
    void fn_00175800(int x, int y);
};

// 0x00175800
void S_00175800::fn_00175800(int x, int y)
{
    a = x;
    b = y;
}

struct S_00175F60
{
    char pad[0x80];
    float v;
    void fn_00175F60(float x);
};

// 0x00175F60
void S_00175F60::fn_00175F60(float x)
{
    v = x;
}
