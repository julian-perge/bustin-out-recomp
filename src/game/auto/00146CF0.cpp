struct S_00146CF0Node
{
    char pad[16];
    S_00146CF0Node* next;
};
struct S_00146CF0
{
    S_00146CF0Node* head;
    int fn_00146CF0();
};
// 0x00146CF0
int S_00146CF0::fn_00146CF0()
{
    int n = 0;
    for (S_00146CF0Node* p = head; p; p = p->next)
        n++;
    return n;
}
