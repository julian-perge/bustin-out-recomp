struct A { virtual void a0(); };
struct B { virtual void b0(); };
struct C {
    virtual void c0(); virtual void c1(); virtual void c2(); virtual void c3();
    virtual void c4(); virtual void c5(); virtual void c6(); virtual void c7();
    virtual void c8(); virtual void c9(); virtual void c10(); virtual int c11();
};
struct S_0018E580 : virtual A, virtual B, virtual C {
    int FUN_0018e580();
};
// 0x0018E580
// parked: unclassified
int S_0018E580::FUN_0018e580()
{
    return this ? C::c11() : 0;
}
