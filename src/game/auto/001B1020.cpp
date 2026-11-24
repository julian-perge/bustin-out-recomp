struct S_001B1020_elem
{
    char d[12];
};

struct S_001B1020
{
    S_001B1020_elem* first;
    S_001B1020_elem* last;
    int FUN_001b1020();
};

// 0x001B1020
int S_001B1020::FUN_001b1020()
{
    return last - first;
}
