struct S_001D9A10_P
{
    int a;
    int b;
};

struct S_001D9A10
{
    int pad[25];
    int x;
    int y;
    void FUN_001D9A10(const S_001D9A10_P* p);
};

// 0x001D9A10
void S_001D9A10::FUN_001D9A10(const S_001D9A10_P* p)
{
    x = p->a;
    y = p->b;
}
