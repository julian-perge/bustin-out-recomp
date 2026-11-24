struct S_00188350Node
{
    char pad[16];
    S_00188350Node* next;
};
struct S_00188350
{
    S_00188350Node* head;
    int fn_00188350();
};
// 0x00188350
int S_00188350::fn_00188350()
{
    int n = 0;
    for (S_00188350Node* p = head; p; p = p->next)
        n++;
    return n;
}
