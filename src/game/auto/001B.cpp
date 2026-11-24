struct VB_001B5210
{
    char pad[0x10];
    int f;
};
struct Base_001B5210
{
    char pad[0x20];
};
struct S_001B5210 : Base_001B5210, virtual VB_001B5210
{
    void FUN_001B5210(int v);
};

// 0x001B5210
void S_001B5210::FUN_001B5210(int v)
{
    f = v;
}
