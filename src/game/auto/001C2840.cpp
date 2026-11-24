struct S_001C2840 {
    char pad[6];
    unsigned char a;
    unsigned char b;
    int FUN_001c2840();
};

// 0x001C2840
int S_001C2840::FUN_001c2840()
{
    return ((a + b + 3) & ~3) * 2 + 16;
}
