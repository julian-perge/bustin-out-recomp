struct S_001E9170
{
    short pad[0x210];
    short v[8];
    void FUN_001e9170(short i, short x);
};

// 0x001E9170
void S_001E9170::FUN_001e9170(short i, short x)
{
    v[i] = x;
}
