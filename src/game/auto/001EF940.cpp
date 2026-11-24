struct S_001EF940 {
    struct E { int a; int b; };
    E* data;
    E* FUN_001ef940();
};

// 0x001EF940
S_001EF940::E* S_001EF940::FUN_001ef940()
{
    int n = data ? ((int*)data)[-1] : 0;
    return data + n;
}
