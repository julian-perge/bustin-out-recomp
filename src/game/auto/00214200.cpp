struct S_00214200
{
    char pad[0xc];
    int* arr;
    void FUN_00214200(int* out, int i);
};

// 0x00214200
void S_00214200::FUN_00214200(int* out, int i)
{
    *out = arr[i];
}
