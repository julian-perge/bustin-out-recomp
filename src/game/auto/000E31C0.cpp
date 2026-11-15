#include "UnkTargetBase.h"

// declared: 0x000E3160 Array_000E31C0::~Array_000E31C0

// The container at +0x4C is a vector of pointers that frees its storage through a pool. Its
// destructor is 0x000E3160.
struct Array_000E31C0
{
    Array_000E31C0() { first = 0; last = 0; end = 0; }
    ~Array_000E31C0() throw();

    void* first;
    void* last;
    void* end;
};

// The base of the dialog screens. Its vtable is at 0x002EA260 and takes every slot of
// UnkTargetBase except slot 0. 0x002EA2A8 and 0x002EA840 are the vtables of two classes built on it.
class Dialog_000E31C0 : public UnkTargetBase
{
public:
    Dialog_000E31C0(const char* a1);
    virtual ~Dialog_000E31C0();

    void FUN_000E0830();

    const char* unk44;
    int unk48;
    Array_000E31C0 unk4C;
    bool unk58;
    bool unk59;
};

// 0x000E31C0
Dialog_000E31C0::Dialog_000E31C0(const char* a1) : unk44(a1), unk48(0), unk58(true), unk59(true)
{
}

// 0x000E3200
Dialog_000E31C0::~Dialog_000E31C0()
{
    FUN_000E0830();
}
