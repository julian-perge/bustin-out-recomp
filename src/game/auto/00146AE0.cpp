struct S_00146AE0Node
{
    char pad[16];
    S_00146AE0Node* next;
};
struct S_00146AE0
{
    S_00146AE0Node* head;
    int fn_00146AE0();
};
// 0x00146AE0
int S_00146AE0::fn_00146AE0()
{
    int n = 0;
    for (S_00146AE0Node* p = head; p; p = p->next)
        n++;
    return n;
}
