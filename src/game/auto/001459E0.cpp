struct S_001459E0_in
{
    int a;
    int b;
    int c;
};

struct S_001459E0
{
    int pad[5];
    S_001459E0_in* in;
    bool FUN_001459E0();
};

// 0x001459E0
bool __stdcall FUN_001459E0(S_001459E0* p)
{
    return p->in->c != 0;
}
