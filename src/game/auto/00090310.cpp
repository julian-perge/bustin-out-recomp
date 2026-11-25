struct S_00090310
{
    char pad[0x48];
    void (S_00090310::*handlers[0x34])(int, unsigned);
    void FUN_00090310(int a, unsigned idx);
};

// 0x00090310
void S_00090310::FUN_00090310(int a, unsigned idx)
{
    if (idx < 0x34 && handlers[idx])
        (this->*handlers[idx])(a, idx);
}
