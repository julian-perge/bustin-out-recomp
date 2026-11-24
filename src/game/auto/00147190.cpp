struct S_00147190
{
    char pad[0x34];
    char* limit;
    char* FUN_00147190(char* p);
};

// 0x00147190
char* S_00147190::FUN_00147190(char* p)
{
    char* e = p + (*(unsigned*)(p + 4) >> 3);
    return e < limit ? e : 0;
}
