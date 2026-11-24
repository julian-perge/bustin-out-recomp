struct S_001C2860 {
    char pad[6];
    unsigned char b;
    unsigned char a;
    char* FUN_001c2860();
};

// 0x001C2860
char* S_001C2860::FUN_001c2860()
{
    return (char*)this + ((a + b + 3) & ~3) * 2 + 16;
}
