struct Sub_00125CC0
{
    void FUN_00146f70();
};

struct S_00125CC0
{
    char pad[0x6C];
    Sub_00125CC0 sub;
    void FUN_00125150(int a);
    S_00125CC0* fn_00125CC0();
};

// 0x00125CC0
S_00125CC0* S_00125CC0::fn_00125CC0()
{
    sub.FUN_00146f70();
    FUN_00125150(1);
    return this;
}
