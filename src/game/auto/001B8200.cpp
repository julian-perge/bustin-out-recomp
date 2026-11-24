struct S_001B8200 {
    int a;
    int b;
    unsigned flags;
    void FUN_001b8200(int bit);
};

// 0x001B8200
void S_001B8200::FUN_001b8200(int bit)
{
    flags |= 1 << bit;
}
