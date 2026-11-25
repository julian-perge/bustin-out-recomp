// The unit of 0x0014B490 holds 10 more bytes after the constructor: `mov eax, [ecx]; push eax; call ...; pop ecx; ret`
// at 0x0014B4A0, a function that Ghidra does not have. The source matches the 16 bytes of the constructor only.
struct S_0014B490
{
    int a, b;
    S_0014B490();
};

// 0x0014B490
// parked: unclassified
S_0014B490::S_0014B490()
{
    a = 0;
    b = 0;
}
