struct S_0012D020
{
    char pad0[0x28];
    S_0012D020* next;
    char pad1[0x17fc8 - 0x2c];
    S_0012D020* head;
    void FUN_0012d020(S_0012D020* p);
};

// 0x0012D020
void S_0012D020::FUN_0012d020(S_0012D020* p)
{
    p->next = head;
    head = p;
}
