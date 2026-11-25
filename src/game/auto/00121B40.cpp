struct S_00121B40
{
    char pad[0x4C];
    int* cur;
    void FUN_00121B40(int** next, int* value);
};

// 0x00121B40
void S_00121B40::FUN_00121B40(int** next, int* value)
{
    *value = *cur;
    *next = cur + 1;
}
