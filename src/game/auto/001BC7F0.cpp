// The original takes the destination in ECX and the source in EAX, which no VC71 calling convention gives.
// 0x001BC7F0
// parked: unclassified
void __fastcall FUN_001bc7f0(char* dst, int unused, const short* src)
{
    while (*src) {
        *dst = (char)*src;
        src++;
        dst++;
    }
    *dst = 0;
}
