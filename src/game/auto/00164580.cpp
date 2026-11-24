struct S_00164580
{
    int pad;
    char on;
    bool FUN_00164580(unsigned n);
};

// 0x00164580
bool S_00164580::FUN_00164580(unsigned n)
{
    if (n <= 8 && on)
        return true;
    return false;
}
