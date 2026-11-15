#include "m0_slots.h"

struct C_0014C7B0
{
    M0_SLOTS_75
    virtual unsigned char* Reserve(int count);
    virtual void Begin(int a, int b);
    virtual void End();
    void fn_0014C7B0();
};

// 0x0014C7B0
void C_0014C7B0::fn_0014C7B0()
{
    Begin(0, 0);
    *Reserve(1) = 0x1c;
    End();
}
