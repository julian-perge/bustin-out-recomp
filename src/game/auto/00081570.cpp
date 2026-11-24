struct S_00081570 {
    char pad[0x40];
    void* arg;
    unsigned char (__cdecl* fn)(void*);
    unsigned char FUN_00081570();
};
// 0x00081570
unsigned char S_00081570::FUN_00081570()
{
    if (fn)
        return fn(arg);
    return 0;
}
