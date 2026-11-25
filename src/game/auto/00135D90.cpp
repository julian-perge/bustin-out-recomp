struct S_00135D90_E
{
    int a;
    int v;
    int c;
    int d;
};

struct S_00135D90
{
    char pad[0x20];
    S_00135D90_E* items;
    int count;
    int FUN_00135d90();
};

// 0x00135D90
int S_00135D90::FUN_00135d90()
{
    int sum = 0;
    for (int i = 0; i < count; i++) {
        sum += items[i].v;
    }
    return sum;
}
