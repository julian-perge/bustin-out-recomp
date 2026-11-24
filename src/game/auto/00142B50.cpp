struct S_00142B50Node
{
    char pad[8];
    S_00142B50Node* next;
};
struct S_00142B50
{
    S_00142B50Node* head;
    int fn_00142B50();
};
// 0x00142B50
int S_00142B50::fn_00142B50()
{
    int n = 0;
    for (S_00142B50Node* p = head; p; p = p->next)
        n++;
    return n;
}
