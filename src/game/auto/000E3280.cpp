#include "UnkTargetBase.h"

// declared: 0x000E3160 Array_000E3280::~Array_000E3280
// declared: 0x000E3200 Dialog_000E3280::~Dialog_000E3280
// declared: 0x000E3310 Unk_000E3280::~Unk_000E3280
// declared: 0x000D6090 Unk_000E3280::FUN_00124940
// declared: 0x000D6190 Unk_000E3280::FUN_00124980
// declared: 0x000D6290 Unk_000E3280::FUN_00017CB0
// declared: 0x000D6330 Unk_000E3280::FUN_00017CC0

struct ERC;

extern char DAT_002E3464[];

struct Array_000E3280
{
    Array_000E3280() { first = 0; last = 0; end = 0; }
    ~Array_000E3280() throw();

    void* first;
    void* last;
    void* end;
};

// The base of the dialog screens, built by 0x000E31C0. Its constructor is inline here, as VC71
// inlined it into the constructors of the two classes built on it.
class Dialog_000E3280 : public UnkTargetBase
{
public:
    Dialog_000E3280(const char* a1) : unk44(a1), unk48(0), unk58(true), unk59(true) {}
    virtual ~Dialog_000E3280();

    void FUN_000E0830();

    const char* unk44;
    int unk48;
    Array_000E3280 unk4C;
    bool unk58;
    bool unk59;
};

// The second dialog class (F-0048). Its vtable is at 0x002EA2A8 and overrides slots 0, 1, 2, 7
// and 8 of UnkTargetBase.
class Unk_000E3280 : public Dialog_000E3280
{
public:
    Unk_000E3280(char a1);
    virtual ~Unk_000E3280();
    virtual void FUN_00124940();
    virtual void FUN_00124980(ERC* rc);
    virtual void FUN_00017CB0(int a1, int a2);
    virtual int FUN_00017CC0(int a1);

    char unk5C;
    int unk60;
    int unk64;
    int unk68;
    char unk6C;
    int unk70;
    float unk74;
    float unk78;
    float unk7C;
    float unk80;
    int unk84;
};

// 0x000E3280
// parked: scheduling
Unk_000E3280::Unk_000E3280(char a1)
    : Dialog_000E3280(DAT_002E3464), unk5C(a1), unk60(0), unk64(0), unk68(0), unk6C(0), unk70(0),
      unk74(0.0f), unk78(0.0f), unk7C(0.0f), unk80(0.0f), unk84(0)
{
}
