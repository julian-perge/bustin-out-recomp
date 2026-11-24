struct S_001FD200
{
    char pad[0x38];
    int v;
    void FUN_001fd200(int n);
};

// 0x001FD200
void S_001FD200::FUN_001fd200(int n)
{
    if (n >= 0 && n < 8)
        v = n;
}
