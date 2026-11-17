// generated: 0x00127DA0

void FUN_00123040(void* p);

// The class with the vtable at 0x002ECA00.
class Tracked_00127860
{
public:
    virtual ~Tracked_00127860();
    void operator delete(void* p) { FUN_00123040(p); }
    virtual void FUN_001281F0();
    virtual void FUN_00127890();
    virtual void FUN_001278A0();
    virtual void FUN_001278B0();
    virtual void FUN_001280E0();
    virtual void FUN_001278C0();
};

extern Tracked_00127860* DAT_0035D420;
extern Tracked_00127860* DAT_0035D424;

// 0x00127860
Tracked_00127860::~Tracked_00127860()
{
    if (DAT_0035D420 == this) {
        DAT_0035D420 = 0;
    }
    if (DAT_0035D424 == this) {
        DAT_0035D424 = 0;
    }
}
