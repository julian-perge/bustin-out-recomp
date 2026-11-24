struct S_00179920Node
{
    char pad[16];
    S_00179920Node* next;
};
struct S_00179920
{
    S_00179920Node* head;
    int fn_00179920();
};
// 0x00179920
int S_00179920::fn_00179920()
{
    int n = 0;
    for (S_00179920Node* p = head; p; p = p->next)
        n++;
    return n;
}
