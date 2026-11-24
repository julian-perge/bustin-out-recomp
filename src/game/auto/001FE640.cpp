struct S_001FE640
{
    char pad[0x30];
    void (__cdecl *fn)(int, int, int);
    void FUN_001fe640(int a, int b, int c);
};

// 0x001FE640
void S_001FE640::FUN_001fe640(int a, int b, int c)
{
    fn(a, b, c);
}
