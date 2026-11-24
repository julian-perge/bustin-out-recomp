struct S_0019A900_obj
{
    virtual void v0();
    virtual int FUN_0019a900_slot1(int x);
};

// 0x0019A900
int FUN_0019a900(S_0019A900_obj* p, int x)
{
    if (p)
        return p->FUN_0019a900_slot1(x);
    return 0;
}
