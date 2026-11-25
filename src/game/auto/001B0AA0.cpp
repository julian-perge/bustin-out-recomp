struct S_001B0AA0
{
    int a;
    int b;
    S_001B0AA0* next;
};

// 0x001B0AA0
S_001B0AA0* FUN_001b0aa0(S_001B0AA0* n)
{
    while (n->next) {
        n = n->next;
    }
    return n;
}
