struct S_001B1270
{
    int x;
    char c;
    S_001B1270* FUN_001b1270(const int* px, const char* pc);
};

// 0x001B1270
S_001B1270* S_001B1270::FUN_001b1270(const int* px, const char* pc)
{
    x = *px;
    c = *pc;
    return this;
}
