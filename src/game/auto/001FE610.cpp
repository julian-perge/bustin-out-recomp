struct S_001FE610
{
    char pad[0x20];
    void (*fn)(int, int);
    void FUN_001fe610(int a, int b);
};

// 0x001FE610
void S_001FE610::FUN_001fe610(int a, int b)
{
    fn(a, b);
}
