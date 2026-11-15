struct Sub_00027EF0
{
    int FUN_001469e0(int a, int b);
};

struct S_00027EF0
{
    char pad[0x30];
    Sub_00027EF0 sub;
    bool fn_00027EF0(int a);
};

// 0x00027EF0
bool S_00027EF0::fn_00027EF0(int a)
{
    return sub.FUN_001469e0(a, 0) != 0;
}
