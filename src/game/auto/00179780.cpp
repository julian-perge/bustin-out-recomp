struct S_00179780Node
{
    char pad[16];
    S_00179780Node* next;
};
struct S_00179780
{
    S_00179780Node* head;
    int fn_00179780();
};
// 0x00179780
int S_00179780::fn_00179780()
{
    int n = 0;
    for (S_00179780Node* p = head; p; p = p->next)
        n++;
    return n;
}
