struct S_00193140_u
{
    int pad[2];
    int off;
};

struct S_00193140_t
{
    int pad;
    S_00193140_u* u;
};

struct S_00193140
{
    char pad[0x24];
    S_00193140_t* t;
    char* FUN_00193140();
};

// 0x00193140
char* S_00193140::FUN_00193140()
{
    if (!t)
        return 0;
    return (char*)t + t->u->off + 4;
}
