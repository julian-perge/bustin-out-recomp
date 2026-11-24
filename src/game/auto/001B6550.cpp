struct V1
{
    int a;
};

struct V2
{
    int b;
};

struct V3
{
    int c;
};

struct D : virtual V1, virtual V2, virtual V3
{
    int d;
};

struct S_001B6550
{
    V3* FUN_001b6550();
};

// 0x001B6550
V3* S_001B6550::FUN_001b6550()
{
    return *(D**)((char*)this - 0x70);
}
