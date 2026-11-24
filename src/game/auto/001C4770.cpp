struct S_001C4770_N {
    int a;
    S_001C4770_N* next;
};
struct S_001C4770 {
    S_001C4770_N* head;
    int FUN_001c4770();
};

// 0x001C4770
int S_001C4770::FUN_001c4770()
{
    int n = 0;
    for (S_001C4770_N* p = head; p; p = p->next)
        n++;
    return n;
}
