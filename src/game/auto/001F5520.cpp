struct S_001F5520_node
{
    char pad[0x1c];
    S_001F5520_node* next;
};

struct S_001F5520
{
    char pad[0x408];
    S_001F5520_node* head;
    void FUN_001f5520(S_001F5520_node* n);
};

// 0x001F5520
void S_001F5520::FUN_001f5520(S_001F5520_node* n)
{
    n->next = head;
    head = n;
}
