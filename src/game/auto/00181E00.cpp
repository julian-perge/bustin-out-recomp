struct S_00181E00Node
{
    char pad[4];
    S_00181E00Node* next;
};
struct S_00181E00
{
    S_00181E00Node* head;
    int fn_00181E00();
};
// 0x00181E00
int S_00181E00::fn_00181E00()
{
    int n = 0;
    for (S_00181E00Node* p = head; p; p = p->next)
        n++;
    return n;
}
