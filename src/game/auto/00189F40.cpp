struct S_00189F40Item
{
    int pad[2];
    void *v;
};

struct S_00189F40
{
    char pad[0x12c];
    S_00189F40Item *items[1];
    bool FUN_00189f40(int i);
};

// 0x00189F40
bool S_00189F40::FUN_00189f40(int i)
{
    return items[i]->v;
}
