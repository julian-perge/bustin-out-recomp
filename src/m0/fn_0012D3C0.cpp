struct Node_0012D3C0
{
    int m_value;
    int m_4;
    Node_0012D3C0* m_next;
};

struct List_0012D3C0
{
    Node_0012D3C0* m_head;
};

struct C_0012D3C0
{
    char m_pad[0x12fbc];
    int m_items[(0x157bc - 0x12fbc) / 4];
    int m_count;
    void fn_0012D3C0(List_0012D3C0* list);
};

// 0x0012D3C0
void C_0012D3C0::fn_0012D3C0(List_0012D3C0* list)
{
    for (Node_0012D3C0* node = list->m_head; node; node = node->m_next)
        m_items[m_count++] = node->m_value;
}
