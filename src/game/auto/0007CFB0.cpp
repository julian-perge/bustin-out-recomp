#include "UnkTargetBase.h"

// declared: 0x0007D490 HouseSelect_0007CFB0::FUN_00124940
// declared: 0x0007CC20 HouseSelect_0007CFB0::FUN_00124980
// declared: 0x00078E30 HouseSelect_0007CFB0::FUN_00017CB0
// declared: 0x0007A260 HouseSelect_0007CFB0::FUN_00017CC0
// declared: 0x0007CCD0 Array_0007CFB0::~Array_0007CFB0

struct ERC;

void FUN_00123040(void* p);

struct Array_0007CFB0
{
    ~Array_0007CFB0() throw();

    void* first;
    void* last;
    void* end;
};

// The HouseSelect screen (F-0039). Its vtable is at 0x002E5728 and overrides slots 0, 1, 2, 7 and 8
// of UnkTargetBase. The call in the destructor is ShutdownHouseSelectScreen, 0x00079F30.
class HouseSelect_0007CFB0 : public UnkTargetBase
{
public:
    virtual ~HouseSelect_0007CFB0();
    virtual void FUN_00124940();
    virtual void FUN_00124980(ERC* rc);
    virtual void FUN_00017CB0(int a1, int a2);
    virtual int FUN_00017CC0(int a1);

    void operator delete(void* p) { FUN_00123040(p); }

    void FUN_00079F30();

    char pad44[0x12C - 0x44];
    Array_0007CFB0 unk12C;
};

// 0x0007CFB0
HouseSelect_0007CFB0::~HouseSelect_0007CFB0()
{
    FUN_00079F30();
}
