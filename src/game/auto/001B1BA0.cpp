struct S_001B1BA0_node
{
    char c;
    int a;
    S_001B1BA0_node* l;
    S_001B1BA0_node* r;
};

struct S_001B1BA0
{
    S_001B1BA0_node* head;
    void FUN_001B1BA0();
};

// 0x001B1BA0
void S_001B1BA0::FUN_001B1BA0()
{
    head->c = 0;
    head->a = 0;
    head->l = head;
    head->r = head;
}
