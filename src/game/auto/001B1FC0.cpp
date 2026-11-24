struct S_001B1FC0
{
    int x;
    char c;
    S_001B1FC0* FUN_001b1fc0(const int* px, const char* pc);
};

// 0x001B1FC0
S_001B1FC0* S_001B1FC0::FUN_001b1fc0(const int* px, const char* pc)
{
    x = *px;
    c = *pc;
    return this;
}
