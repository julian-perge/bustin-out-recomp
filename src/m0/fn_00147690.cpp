struct C_00147690
{
    virtual void s000();
    virtual void Enter(int timeout);
    virtual void s002();
    virtual void Leave();
    char m_pad[0x28 - 4];
    unsigned int m_28;
    bool fn_00147690(unsigned int n);
};

// 0x00147690
bool C_00147690::fn_00147690(unsigned int n)
{
    Enter(-1);
    bool result = m_28 >= n;
    Leave();
    return result;
}
