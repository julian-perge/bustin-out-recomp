struct S_00214170
{
    char pad[0xc];
    int* arr;
    void FUN_00214170(int* out, int i);
};

// 0x00214170
void S_00214170::FUN_00214170(int* out, int i)
{
    *out = arr[i];
}
