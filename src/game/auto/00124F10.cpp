struct S_00124F10_in { char pad[0x10]; unsigned int flags; };
struct S_00124F10 { int pad; S_00124F10_in* p; bool FUN_00124f10(unsigned int m); };
// 0x00124F10
bool S_00124F10::FUN_00124f10(unsigned int m)
{
    if ((p->flags & m) == m)
        return true;
    return false;
}
