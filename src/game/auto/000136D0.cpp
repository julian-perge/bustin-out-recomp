void* FUN_00123060(unsigned int size, int align);

// 0x000136D0
void* operator new(unsigned int size)
{
    return FUN_00123060(size, 4);
}
