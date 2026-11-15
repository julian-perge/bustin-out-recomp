#include "UnkTargetBase.h"

// declared: 0x00097320 LoadBar_00097300::~LoadBar_00097300
// declared: 0x00097390 LoadBar_00097300::FUN_00124940
// declared: 0x000973B0 LoadBar_00097300::FUN_00124980
// declared: 0x000975C0 LoadBar_00097300::FUN_00017CB0
// declared: 0x000975F0 LoadBar_00097300::FUN_00017CC0

struct ERC;

// The load-bar screen. Its vtable is at 0x002E6A88 and overrides slots 0, 1, 2, 7 and 8 of
// UnkTargetBase (F-0042).
class LoadBar_00097300 : public UnkTargetBase
{
public:
    LoadBar_00097300();
    virtual ~LoadBar_00097300();
    virtual void FUN_00124940();
    virtual void FUN_00124980(ERC* rc);
    virtual void FUN_00017CB0(int a1, int a2);
    virtual int FUN_00017CC0(int a1);

    char unk44;
    int unk48;
    int unk4C;
    char unk50;
};

// 0x00097300
LoadBar_00097300::LoadBar_00097300()
{
    unk44 = 0;
    unk48 = 0;
    unk50 = 0;
}
