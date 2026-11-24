struct S_001FF9C0
{
    S_001FF9C0* next;
};

struct S_001FF9C0_List
{
    char pad[0x110];
    S_001FF9C0* head;
    void FUN_001ff9c0(S_001FF9C0* n);
};

// 0x001FF9C0
void S_001FF9C0_List::FUN_001ff9c0(S_001FF9C0* n)
{
    n->next = head;
    head = n;
}
