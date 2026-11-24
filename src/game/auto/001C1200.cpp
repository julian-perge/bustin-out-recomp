struct S_001C1200 {
    struct E { int a; int b; };
    E* data;
    E* FUN_001c1200();
};

// 0x001C1200
S_001C1200::E* S_001C1200::FUN_001c1200()
{
    int n = data ? ((int*)data)[-1] : 0;
    return data + n;
}
