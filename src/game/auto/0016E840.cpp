struct S_0016E840
{
    int a, b;
    void FUN_0016E840(int** pp);
};

// 0x0016E840
void S_0016E840::FUN_0016E840(int** pp)
{
    a = **pp;
    *pp += 1;
    b = **pp;
    *pp += 1;
}
