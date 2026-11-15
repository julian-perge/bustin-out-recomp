struct S_001231F0
{
    virtual void v0();
    virtual void v1(int a);
    void fn_001231F0(char c);
};

// 0x001231F0
void S_001231F0::fn_001231F0(char c)
{
    v1(c ? -1 : 0);
}

struct S_00128AE0
{
    virtual ~S_00128AE0();
};

// 0x00128AE0
void __stdcall fn_00128AE0(S_00128AE0* p, int b)
{
    if (p)
        delete p;
}

struct S_0012AC00
{
    char pad[0x114];
    float v114;
    char pad2[0x0C];
    float v124;
    void fn_0012AC00(float x);
    void fn_0012AC20(float x);
};

// 0x0012AC00
void S_0012AC00::fn_0012AC00(float x)
{
    v114 = x;
}

// 0x0012AC20
void S_0012AC00::fn_0012AC20(float x)
{
    v124 = x;
}
