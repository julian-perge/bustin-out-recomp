struct S_00143EF0Elem { int d[15]; };
struct S_00143EF0
{
    S_00143EF0Elem* p;
    S_00143EF0Elem* fn_00143EF0(int i);
};
// 0x00143EF0
S_00143EF0Elem* S_00143EF0::fn_00143EF0(int i)
{
    return p + i;
}
