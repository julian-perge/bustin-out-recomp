struct S_002140D0
{
    char pad[0xc];
    int* arr;
    void FUN_002140d0(int* out, int i);
};

// 0x002140D0
void S_002140D0::FUN_002140d0(int* out, int i)
{
    *out = arr[i];
}
