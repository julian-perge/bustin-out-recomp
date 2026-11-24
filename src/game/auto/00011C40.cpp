struct S_00011C40
{
    int pad;
    int a;
    int b;
    int* p;
    void FUN_00011c40(int* q);
};

// 0x00011C40
void S_00011C40::FUN_00011c40(int* q)
{
    p = q;
    a = *q;
    b = a + 0x80;
}
