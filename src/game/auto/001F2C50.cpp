struct S_001F2C50
{
    int a;
    int b;
    S_001F2C50* FUN_001f2c50(const int* p, const int* q);
};

// 0x001F2C50
S_001F2C50* S_001F2C50::FUN_001f2c50(const int* p, const int* q)
{
    a = *p;
    b = *q;
    return this;
}
