struct S_0005EBA0Elem { int d[15]; };
struct S_0005EBA0
{
    S_0005EBA0Elem* p;
    S_0005EBA0Elem* fn_0005EBA0(int i);
};
// 0x0005EBA0
S_0005EBA0Elem* S_0005EBA0::fn_0005EBA0(int i)
{
    return p + i;
}
