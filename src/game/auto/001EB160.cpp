struct E_001EB160
{
    char d[20];
};

struct S_001EB160
{
    E_001EB160* b;
    E_001EB160* m;
    E_001EB160* e;
    int FUN_001eb160();
};

// 0x001EB160
int S_001EB160::FUN_001eb160()
{
    return e - b;
}
