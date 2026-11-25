struct S_001B0AC0
{
    int a;
    int b;
    int c;
    S_001B0AC0* next;
};

// 0x001B0AC0
S_001B0AC0* FUN_001b0ac0(S_001B0AC0* n)
{
    while (n->next) {
        n = n->next;
    }
    return n;
}
