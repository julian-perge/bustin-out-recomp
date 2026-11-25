struct S_001550A0
{
    char pad[0x18];
    S_001550A0* next;
    bool FUN_001550a0(S_001550A0* p);
};

// 0x001550A0
bool S_001550A0::FUN_001550a0(S_001550A0* p)
{
    S_001550A0* s = this;
    do {
        if (s == p)
            return true;
        s = s->next;
    } while (s);
    return false;
}
