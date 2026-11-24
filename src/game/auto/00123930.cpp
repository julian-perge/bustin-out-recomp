struct S_00123930
{
    char pad[0x18];
    void* p;
    void fn_00123930(void* o);
};
// 0x00123930
void S_00123930::fn_00123930(void* o)
{
    if (p == o)
        p = 0;
}
