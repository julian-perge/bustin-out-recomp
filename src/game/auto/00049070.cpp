struct Obj_00049070
{
    void FUN_00153ad0();
};

struct Node_00049070
{
    Obj_00049070* obj;
    int pad;
    Node_00049070* next;
};

struct S_00049070
{
    char pad[0x24];
    Node_00049070* head;
    void fn_00049070();
};

// 0x00049070
void S_00049070::fn_00049070()
{
    for (Node_00049070* n = head; n; n = n->next)
        n->obj->FUN_00153ad0();
}
