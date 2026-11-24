struct S_001F2A60
{
    int a;
    int b;
    S_001F2A60* FUN_001f2a60(const int* p, const int* q);
};

// 0x001F2A60
S_001F2A60* S_001F2A60::FUN_001f2a60(const int* p, const int* q)
{
    a = *p;
    b = *q;
    return this;
}
