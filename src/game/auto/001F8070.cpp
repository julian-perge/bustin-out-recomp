struct P_001F8070
{
    char pad[0x48];
    int h;
};

// 0x001F8070
int __stdcall FUN_001f8070(P_001F8070* p)
{
    return (p->h + 23) % 24;
}
