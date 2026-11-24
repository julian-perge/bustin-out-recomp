struct S_00181140Node
{
    char pad[16];
    S_00181140Node* next;
};
struct S_00181140
{
    S_00181140Node* head;
    int fn_00181140();
};
// 0x00181140
int S_00181140::fn_00181140()
{
    int n = 0;
    for (S_00181140Node* p = head; p; p = p->next)
        n++;
    return n;
}
