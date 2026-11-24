struct S_00200380_node
{
    char c;
    int a;
    S_00200380_node* l;
    S_00200380_node* r;
};

struct S_00200380
{
    S_00200380_node* head;
    void FUN_00200380();
};

// 0x00200380
void S_00200380::FUN_00200380()
{
    head->c = 0;
    head->a = 0;
    head->l = head;
    head->r = head;
}
