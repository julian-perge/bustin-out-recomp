struct S_002140B0
{
    char pad[0xc];
    int* arr;
    void FUN_002140b0(int* out, int i);
};

// 0x002140B0
void S_002140B0::FUN_002140b0(int* out, int i)
{
    *out = arr[i];
}
