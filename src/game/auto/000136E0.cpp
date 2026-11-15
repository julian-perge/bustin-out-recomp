void FUN_00123040(void* p);

// 0x000136E0
void operator delete(void* p)
{
    FUN_00123040(p);
}
