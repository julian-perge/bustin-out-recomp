struct S_0019B2A0
{
    int key;
    int pad;
    S_0019B2A0* next;
};

// The original takes the list head in EAX, which no calling convention of VC71 gives (F-0121).
// 0x0019B2A0
// parked: unclassified
// The original takes the list head in EAX and the key in ECX, which no VC71 calling convention gives.
bool __fastcall FUN_0019b2a0(int key, S_0019B2A0** head)
{
    for (S_0019B2A0* n = *head; n; n = n->next)
        if (n->key == key)
            return true;
    return false;
}
