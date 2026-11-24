struct S_00189750
{
    int pad[2];
    char on;
};

// 0x00189750
int FUN_00189750(const S_00189750* p)
{
    if (p && p->on)
        return 1;
    return 0;
}
