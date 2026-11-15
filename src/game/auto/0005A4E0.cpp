#include "UnkTargetBase.h"

// declared: 0x00059DB0 Unk_0005A4E0::~Unk_0005A4E0
// declared: 0x00059EA0 Unk_0005A4E0::FUN_00124940
// declared: 0x00059240 Unk_0005A4E0::FUN_00124980
// declared: 0x000588D0 Unk_0005A4E0::FUN_00017C90

struct ERC;

struct List_0005A4E0
{
    List_0005A4E0()
    {
        tail = 0;
        head = 0;
        owns = 1;
    }
    ~List_0005A4E0() { FUN_00142B90(); }
    void FUN_00142B90();

    void* head;
    void* tail;
    char owns;
};

// A screen with a vtable at 0x002E4390. It overrides slots 0, 1, 2 and 6 of UnkTargetBase.
class Unk_0005A4E0 : public UnkTargetBase
{
public:
    Unk_0005A4E0(int player);
    virtual ~Unk_0005A4E0();
    virtual void FUN_00124940();
    virtual void FUN_00124980(ERC* rc);
    virtual void FUN_00017C90(int sender, int message);

    int unk44;
    List_0005A4E0 unk48;
    int unk54;
    char unk58;
};

// 0x0005A4E0
Unk_0005A4E0::Unk_0005A4E0(int player)
{
    this->player = player;
    unk58 = 0;
    unk54 = 0;
    unk44 = 0;
    SetFlags(0x10, true);
    SetFlags(6, false);
}
