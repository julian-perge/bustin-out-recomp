#include "UnkTargetBase.h"

// declared: 0x000E3160 Array_000F0DE0::~Array_000F0DE0
// declared: 0x000E3200 Dialog_000F0DE0::~Dialog_000F0DE0
// declared: 0x000F0E60 Unk_000F0DE0::~Unk_000F0DE0
// declared: 0x000DA940 Unk_000F0DE0::FUN_00124940
// declared: 0x000D7910 Unk_000F0DE0::FUN_00124980
// declared: 0x000D7DC0 Unk_000F0DE0::FUN_00017CB0
// declared: 0x000D8030 Unk_000F0DE0::FUN_00017CC0

struct ERC;

extern char DAT_002E3464[];

struct Array_000F0DE0
{
    Array_000F0DE0() { first = 0; last = 0; end = 0; }
    ~Array_000F0DE0() throw();

    void* first;
    void* last;
    void* end;
};

// The base of the dialog screens, built by 0x000E31C0. Its constructor is inline here, as VC71
// inlined it into the constructors of the two classes built on it.
class Dialog_000F0DE0 : public UnkTargetBase
{
public:
    Dialog_000F0DE0(const char* a1) : unk44(a1), unk48(0), unk58(true), unk59(true) {}
    virtual ~Dialog_000F0DE0();

    void FUN_000E0830();

    const char* unk44;
    int unk48;
    Array_000F0DE0 unk4C;
    bool unk58;
    bool unk59;
};

// The memory-unit screen (F-0047). Its vtable is at 0x002EA840 and overrides slots 0, 1, 2, 7 and 8
// of UnkTargetBase.
class Unk_000F0DE0 : public Dialog_000F0DE0
{
public:
    Unk_000F0DE0();
    virtual ~Unk_000F0DE0();
    virtual void FUN_00124940();
    virtual void FUN_00124980(ERC* rc);
    virtual void FUN_00017CB0(int a1, int a2);
    virtual int FUN_00017CC0(int a1);

    int unk5C;
    int unk60;
    char pad64[0x78 - 0x64];
    bool unk78;
    bool unk79;
    char pad7A[0xA4 - 0x7A];
    int unkA4;
    int unkA8;
    int unkAC;
    int unkB0;
    int unkB4;
};

// 0x000F0DE0
Unk_000F0DE0::Unk_000F0DE0()
    : Dialog_000F0DE0(DAT_002E3464), unk5C(0), unk60(0), unk78(false), unk79(false), unkA4(0), unkA8(0),
      unkAC(0), unkB0(0), unkB4(0)
{
}
