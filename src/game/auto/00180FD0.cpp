struct S_00180FD0Node
{
    char pad[16];
    S_00180FD0Node* next;
};
struct S_00180FD0
{
    S_00180FD0Node* head;
    int fn_00180FD0();
};
// 0x00180FD0
int S_00180FD0::fn_00180FD0()
{
    int n = 0;
    for (S_00180FD0Node* p = head; p; p = p->next)
        n++;
    return n;
}
