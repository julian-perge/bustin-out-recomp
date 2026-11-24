struct S_0018E500
{
    char pad[0x14];
    short a;
    short b;
    int FUN_0018e500();
};

// 0x0018E500
int S_0018E500::FUN_0018e500()
{
    if (a && b == -1)
        return 1;
    return 0;
}
