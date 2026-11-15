struct S_00165310
{
    virtual ~S_00165310();
};

// 0x00165310
void __stdcall fn_00165310(S_00165310* p, int b)
{
    if (p)
        delete p;
}

struct S_00165390
{
    virtual ~S_00165390();
};

// 0x00165390
void __stdcall fn_00165390(S_00165390* p, int b)
{
    if (p)
        delete p;
}

struct S_00165F20
{
    char pad[4];
    char flag;
    bool fn_00165F20();
};

// 0x00165F20
// parked: unclassified
bool S_00165F20::fn_00165F20()
{
    if (!flag)
        return false;
    flag = 0;
    return true;
}

struct S_0016A600
{
    const char* s;
    int fn_0016A600();
};

// 0x0016A600
int S_0016A600::fn_0016A600()
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
