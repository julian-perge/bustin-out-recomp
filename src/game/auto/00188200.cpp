struct S_00188200Node
{
    char pad[16];
    S_00188200Node* next;
};
struct S_00188200
{
    S_00188200Node* head;
    int fn_00188200();
};
// 0x00188200
int S_00188200::fn_00188200()
{
    int n = 0;
    for (S_00188200Node* p = head; p; p = p->next)
        n++;
    return n;
}
