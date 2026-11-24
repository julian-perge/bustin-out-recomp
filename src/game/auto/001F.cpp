// 0x001F5EA0
void FUN_001F5EA0(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

// 0x001F5EC0
void FUN_001F5EC0(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

struct VB_001F8AA0
{
    char pad[0x14];
    int f;
};
struct Base_001F8AA0
{
    char pad[0x20];
};
struct S_001F8AA0 : Base_001F8AA0, virtual VB_001F8AA0
{
    void FUN_001F8AA0(int v);
};

// 0x001F8AA0
void S_001F8AA0::FUN_001F8AA0(int v)
{
    f = v;
}

struct S_001F1F30
{
    char flag;
    char pad[3];
    int count;
    bool FUN_001F1F30();
};

// 0x001F1F30
bool S_001F1F30::FUN_001F1F30()
{
    if (flag) {
        count += 1;
        return true;
    }
    return true;
}

// 0x001F8F10
void fn_001F8F10(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

// 0x001F8F70
void fn_001F8F70(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

// 0x001FF4A0
void fn_001FF4A0(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

// 0x001FF900
void fn_001FF900(unsigned* dst, const unsigned* src)
{
    if (dst)
        *dst = *src;
}

struct VB_001FB630
{
    char pad[0xc];
    int f;
};
struct Base_001FB630
{
    char pad[0x20];
};
struct S_001FB630 : Base_001FB630, virtual VB_001FB630
{
    void fn_001FB630(int v);
};

// 0x001FB630
void S_001FB630::fn_001FB630(int v)
{
    f = v;
}

struct S_001FE3D0
{
    char pad[0x10];
    int a;
    int b;
    void fn_001FE3D0(int x, int y);
};

// 0x001FE3D0
void S_001FE3D0::fn_001FE3D0(int x, int y)
{
    a = x;
    b = y;
}

struct S_001FE8E0
{
    virtual void v0();
    virtual void v1();
    virtual void v2();
    virtual void v3();
    virtual void v4();
    virtual void v5();
    virtual void v6();
    virtual void v7();
    virtual void v8();
    virtual void v9();
    virtual void v10();
    virtual void v11();
    virtual void v12();
    virtual void v13(int id, int a, int b);
    void fn_001FE8E0(int a);
    void fn_001FE900(int a);
    void fn_001FE920(int a);
};

// 0x001FE8E0
void S_001FE8E0::fn_001FE8E0(int a)
{
    v13(0x13, a, 0);
}

// 0x001FE900
void S_001FE8E0::fn_001FE900(int a)
{
    v13(0x15, a, 0);
}

// 0x001FE920
void S_001FE8E0::fn_001FE920(int a)
{
    v13(0x14, a, 0);
}

struct S_001FEB60Inner
{
    virtual void v0();
    virtual void v1();
    virtual void v2();
    virtual void v3();
    virtual void v4();
    virtual void v5();
    virtual void v6();
    virtual void v7();
    virtual void v8();
    virtual void v9();
    virtual void v10();
    virtual void v11();
    virtual void v12();
    virtual void v13();
    virtual void v14();
    virtual void v15();
    virtual void v16();
    virtual void v17();
    virtual void v18();
    virtual void v19();
    virtual void v20();
    virtual void v21();
    virtual void v22();
    virtual void v23();
    virtual void v24();
    virtual void v25();
    virtual void v26();
    virtual void v27();
    virtual void v28();
    virtual void v29();
    virtual void v30();
    virtual void v31();
    virtual void v32();
    virtual void v33();
    virtual void v34();
    virtual void v35();
    virtual void v36();
    virtual void v37();
    virtual void v38();
    virtual void v39();
    virtual void v40();
    virtual void v41();
    virtual void v42();
    virtual void v43();
};

struct S_001FEB60
{
    char pad[0xbc];
    S_001FEB60Inner* inner;
    void fn_001FEB60(int);
};

// 0x001FEB60
void S_001FEB60::fn_001FEB60(int)
{
    inner->v43();
}

struct S_001F1EE0
{
    int v;
    bool FUN_001F1EE0(const S_001F1EE0& o) const;
};

// 0x001F1EE0
bool S_001F1EE0::FUN_001F1EE0(const S_001F1EE0& o) const
{
    return v != o.v;
}

struct S_001F28A0
{
    char pad[4];
    bool set;
    float val;
    void FUN_001F28A0(float f);
};

// 0x001F28A0
void S_001F28A0::FUN_001F28A0(float f)
{
    set = true;
    val = f;
}

struct S_001F5BF0
{
    unsigned data[256];
    S_001F5BF0();
};

// 0x001F5BF0
S_001F5BF0::S_001F5BF0()
{
    for (int i = 0; i < 256; i++)
        data[i] = 0;
}

struct S_001FE370
{
    int v;
    bool FUN_001FE370(const S_001FE370& o) const;
};

// 0x001FE370
bool S_001FE370::FUN_001FE370(const S_001FE370& o) const
{
    return v == o.v;
}

struct S_001FE540
{
    int a;
    int b;
    S_001FE540(int x);
};

// 0x001FE540
S_001FE540::S_001FE540(int x)
{
    a = x;
    b = 0;
}
