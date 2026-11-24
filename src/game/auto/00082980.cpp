struct S_00082980_E
{
    char pad[28];
};

struct S_00082980
{
    S_00082980_E* p;
    S_00082980_E* FUN_00082980(int n);
};

// 0x00082980
S_00082980_E* S_00082980::FUN_00082980(int n)
{
    return p + n;
}
