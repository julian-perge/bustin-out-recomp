struct S_001430E0 {
    char pad[0x48];
    unsigned int a;
    int b;
    void FUN_001430e0(int x, unsigned int y);
};
// 0x001430E0
void S_001430E0::FUN_001430e0(int x, unsigned int y)
{
    b = x;
    a = y >> 2;
}
