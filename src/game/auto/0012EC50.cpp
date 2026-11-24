extern "C" float sinf(float);
extern "C" float cosf(float);

// 0x0012EC50
// parked: source shape
void __cdecl FUN_0012ec50(float x, float* s, float* c)
{
    *s = sinf(x);
    *c = cosf(x);
}
