struct S_00154AB0Node
{
    char pad[4];
    S_00154AB0Node* next;
};
struct S_00154AB0
{
    S_00154AB0Node* head;
    int fn_00154AB0();
};
// 0x00154AB0
int S_00154AB0::fn_00154AB0()
{
    int n = 0;
    for (S_00154AB0Node* p = head; p; p = p->next)
        n++;
    return n;
}
