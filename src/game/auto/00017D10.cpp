#include "UnkTargetBase.h"

// declared: 0x00017DA0 Unk_00017D10::FUN_00124940
// declared: 0x00017E90 Unk_00017D10::FUN_00124980

struct ERC;

class Registry_00017D10
{
public:
    void FUN_00122E80(unsigned int name);
};

extern Registry_00017D10 DAT_0035DB68;

// A screen with a vtable at 0x002E2438 that overrides slots 0, 1 and 2 of UnkTargetBase.
class Unk_00017D10 : public UnkTargetBase
{
public:
    virtual ~Unk_00017D10();
    virtual void FUN_00124940();
    virtual void FUN_00124980(ERC* rc);

    char pad44[0x58 - 0x44];
    int unk58;
};

// The unit of 0x00017D10 holds 3 more bytes after the destructor: `mov eax, ecx; ret` at 0x00017D70, a
// function that Ghidra does not have. The source matches the 96 bytes of the destructor only.
// 0x00017D10
// parked: unclassified
Unk_00017D10::~Unk_00017D10()
{
    DAT_0035DB68.FUN_00122E80(0x6D1F0956);
    unk58 = 0;
}
