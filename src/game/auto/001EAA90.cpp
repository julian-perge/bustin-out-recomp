struct S_001EAA90
{
    char pad[0x20];
    unsigned m;
    bool FUN_001eaa90(int n);
};

// 0x001EAA90
bool S_001EAA90::FUN_001eaa90(int n)
{
    return (m & (1u << n)) ? true : false;
}
