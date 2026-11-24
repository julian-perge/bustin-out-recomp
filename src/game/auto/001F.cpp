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
