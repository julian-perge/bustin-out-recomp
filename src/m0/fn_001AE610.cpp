#include "m0_slots.h"

struct Sink_001AE610
{
    M0_SLOTS_71
    virtual void Put(int value);
};

struct VBase1_001AE610
{
    virtual void s000();
};

struct VBase2_001AE610
{
    M0_SLOTS_110
    virtual short Get(int which);
};

struct Mid_001AE610 : virtual VBase1_001AE610, virtual VBase2_001AE610
{
    virtual void m000();
    char m_pad[0xb0];
    Sink_001AE610* m_sink;
    char m_pad2[0x154 - 0xbc];
};

struct Iface_001AE610
{
    virtual void fn_001AE610();
};

struct D_001AE610 : Mid_001AE610, Iface_001AE610
{
    void fn_001AE610();
};

// 0x001AE610
void D_001AE610::fn_001AE610()
{
    m_sink->Put(Get(1));
}
