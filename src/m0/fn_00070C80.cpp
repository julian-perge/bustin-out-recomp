struct Base_00070C80
{
    virtual void s000();
    int m_pad[3];
};

struct Iface_00070C80
{
    virtual void s000();
    virtual void Run();
};

struct Target_00070C80 : Base_00070C80, Iface_00070C80
{
};

struct C_00070C80
{
    char m_pad[0xb8];
    Target_00070C80* m_b8;
    void fn_00070C80();
};

// 0x00070C80
void C_00070C80::fn_00070C80()
{
    m_b8->Run();
}
